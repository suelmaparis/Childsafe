import json
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

from app.services.risk_comparison import compare_risk_assessments

LOGO_PATH = Path(__file__).resolve().parents[1] / 'static' / 'brand' / 'childsafe-logo.png'
BLUE = colors.HexColor('#2563EB')
DARK = colors.HexColor('#17324A')
MUTED = colors.HexColor('#65758A')
BORDER = colors.HexColor('#DFE7EF')
PALE = colors.HexColor('#F5F8FB')
YELLOW = colors.HexColor('#FFF7E5')


def _text(value, fallback='Não fornecido'):
    if value is None or (isinstance(value, str) and not value.strip()):
        return fallback
    return str(value)


def _date(value):
    return value.strftime('%d/%m/%Y %H:%M') if value else 'Não fornecido'


def _parsed_reasons(raw):
    try:
        parsed = json.loads(raw or '[]')
    except (ValueError, TypeError):
        parsed = raw
    if isinstance(parsed, list):
        return [str(item) for item in parsed] or ['Não fornecidos']
    return [str(parsed)] if parsed else ['Não fornecidos']


def generate_report_pdf(report, ai_analyses=None, reviews=None, actions=None, evidences=None):
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=38, leftMargin=38,
        topMargin=44, bottomMargin=55,
        title=f'ChildSafe - Denúncia CV-{report.id:06d}', author='ChildSafe',
    )
    width = A4[0] - 76
    styles = {
        'title': ParagraphStyle('CS_Title', fontName='Helvetica-Bold', fontSize=16,
                                leading=21, textColor=DARK, spaceAfter=5),
        'section': ParagraphStyle('CS_Section', fontName='Helvetica-Bold', fontSize=11,
                                  leading=15, textColor=DARK, spaceBefore=10, spaceAfter=8),
        'label': ParagraphStyle('CS_Label', fontName='Helvetica-Bold', fontSize=7.5,
                                leading=10, textColor=MUTED),
        'value': ParagraphStyle('CS_Value', fontName='Helvetica', fontSize=9,
                                leading=13, textColor=DARK, splitLongWords=True),
        'metric': ParagraphStyle('CS_Metric', fontName='Helvetica-Bold', fontSize=15,
                                 leading=19, textColor=DARK, splitLongWords=True),
        'body': ParagraphStyle('CS_Body', fontName='Helvetica', fontSize=8.5,
                               leading=12.5, textColor=DARK, splitLongWords=True),
        'description': ParagraphStyle('CS_Description', fontName='Helvetica', fontSize=8.5,
                                      leading=13, textColor=DARK, borderColor=BORDER,
                                      borderWidth=0.7, borderPadding=10,
                                      spaceBefore=4, spaceAfter=10, splitLongWords=True),
        'small': ParagraphStyle('CS_Small', fontName='Helvetica', fontSize=7.5,
                                leading=11, textColor=MUTED, splitLongWords=True),
    }

    def para(value, style='body'):
        safe = escape(_text(value)).replace('\n', '<br/>')
        return Paragraph(safe, styles[style])

    def url_para(value):
        raw = _text(value)
        parsed = urlparse(raw)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            safe = escape(raw, {'"': '&quot;'})
            return Paragraph(f'<link href="{safe}" color="#185D93">{escape(raw)}</link>',
                             styles['body'])
        return para(raw)

    def card(title, fields, background=colors.white):
        contents = [para(title.upper(), 'label'), Spacer(1, 7)]
        for label, value in fields:
            contents.extend([para(label, 'label'),
                             url_para(value) if label.lower().endswith('url') else para(value, 'value'),
                             Spacer(1, 6)])
        t = Table([[contents]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), background),
            ('BOX', (0, 0), (-1, -1), 0.7, BORDER),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return t

    def metric(label, value, background=PALE):
        t = Table([[[para(label.upper(), 'label'), Spacer(1, 7),
                     para(value, 'metric')]]], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), background),
            ('BOX', (0, 0), (-1, -1), 0.7, BORDER),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 11),
        ]))
        return t

    def row_cards(cards, widths):
        # Every nested card must fit its own column. Without this, ReportLab
        # measures the inner tables at the full page width and clips the right column.
        if len(cards) != len(widths):
            raise ValueError('Card count and column widths must match')
        for inner, outer_width in zip(cards, widths):
            inner_width = outer_width - 8
            inner._argW = [inner_width]
            inner._colWidths = [inner_width]
        t = Table([cards], colWidths=widths, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        return t

    def section(title):
        story.append(para(title, 'section'))

    def details(title, fields):
        section(title)
        for label, value in fields:
            story.append(KeepTogether([para(label, 'label'), para(value, 'body'), Spacer(1, 6)]))

    story = []
    if LOGO_PATH.is_file():
        try:
            from reportlab.lib.utils import ImageReader
            iw, ih = ImageReader(str(LOGO_PATH)).getSize()
            logo_w = 132
            story.append(Image(str(LOGO_PATH), width=logo_w, height=logo_w * ih / iw,
                               hAlign='LEFT'))
            story.append(Spacer(1, 9))
        except Exception:
            pass
    story.extend([para('REPORT REVIEW', 'title'),
                  para(f'CV-{report.id:06d}  |  { _date(getattr(report, "created_at", None)) } UTC', 'small'),
                  Spacer(1, 9), HRFlowable(width='100%', thickness=1, color=BORDER),
                  Spacer(1, 12)])

    confidence = getattr(report, 'detection_confidence', None)
    if confidence is None:
        confidence_text = 'Não fornecido'
    else:
        try:
            n = float(confidence)
            confidence_text = f'{n * 100:.0f}%' if 0 <= n <= 1 else f'{n:.0f}%'
        except (ValueError, TypeError):
            confidence_text = str(confidence)

    story.append(row_cards([
        metric('Risk Level', _text(getattr(report, 'risk_level', None)).upper(),
               colors.HexColor('#FFF5DC')),
        metric('Risk Score', _text(getattr(report, 'risk_score', None)),
               colors.HexColor('#E8F2FF')),
        metric('Confidence', confidence_text, colors.HexColor('#F2E9FC')),
    ], [width / 3] * 3))
    story.append(Spacer(1, 12))

    reviewer = getattr(report, 'assigned_reviewer', None)
    reviewer_name = None
    if reviewer is not None:
        reviewer_name = (getattr(reviewer, 'username', None)
                         or getattr(reviewer, 'name', None)
                         or getattr(reviewer, 'email', None)
                         or f'ID {getattr(reviewer, "id", "?")}')
    if not reviewer_name and getattr(report, 'assigned_reviewer_id', None):
        reviewer_name = f'ID {report.assigned_reviewer_id}'

    cards = [
        card('Report Information', [
            ('Reference', f'CV-{report.id:06d}'),
            ('Platform', getattr(report, 'platform', None)),
            ('Status', getattr(report, 'status', None)),
            ('Created (UTC)', _date(getattr(report, 'created_at', None))),
            ('Source channel', getattr(report, 'source_channel', None)),
            ('Source reference', getattr(report, 'source_reference', None)),
        ]),
        card('Geographic Information', [
            ('Incident location', getattr(report, 'incident_location', None)),
            ('Reporter location', getattr(report, 'reporter_location', None)),
            ('Latitude', getattr(report, 'geo_latitude', None)),
            ('Longitude', getattr(report, 'geo_longitude', None)),
            ('Full location', getattr(report, 'geo_location_text', None)),
            ('Geo source', getattr(report, 'geo_source', None)),
            ('Verification status', getattr(report, 'geo_verification_status', None)),
        ]),
        card('Automated Detection', [
            ('Detection source', getattr(report, 'detection_source', None)),
            ('Confidence', confidence_text),
            ('Signals', getattr(report, 'detection_signals', None)),
            ('School signals', getattr(report, 'school_signals', None)),
        ]),
        card('Review Assignment', [
            ('Assigned reviewer', reviewer_name),
            ('Review status', getattr(report, 'review_status', None)),
        ]),
    ]
    for a, b in ((0, 2), (2, 4)):
        story.append(row_cards(cards[a:b], [width / 2, width / 2]))
        story.append(Spacer(1, 6))

    story.append(row_cards([
        metric('Signal Score', _text(getattr(report, 'detection_signal_score', None))),
        card('Reason', [('Reason', getattr(report, 'reason', None))]),
        card('Report URL', [('Report URL', getattr(report, 'url', None))]),
    ], [width / 3] * 3))
    section('Description')
    story.append(para(getattr(report, 'description', None), 'description'))

    section('Geographic verification notice')
    story.append(para('AVISO: As referências geográficas identificadas automaticamente são indícios preliminares. '
                      'A menção de uma cidade, ilha ou instituição não confirma que o incidente tenha ocorrido '
                      'nesse local. As coordenadas devem ser interpretadas de acordo com a sua origem e '
                      'sujeitas a verificação humana.'))

    section('AI Assessment')
    warning = Table([[para('AI risk scores may reflect a situation reported by a third party, not necessarily '
                           'direct exposure caused by the publication being reviewed. AI assessments are '
                           'preliminary and require human verification.', 'body')]], colWidths=[width])
    warning.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), YELLOW),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.extend([warning, Spacer(1, 10)])

    analyses = list(ai_analyses or [])
    if not analyses:
        story.append(para('Não existem avaliações automáticas registadas.'))
    for index, analysis in enumerate(analyses):
        if index:
            story.append(Spacer(1, 12))
        comparison = None
        try:
            comparison = compare_risk_assessments(
                str(report.risk_level).lower(), int(report.risk_score),
                str(analysis.level).lower(), int(analysis.score),
            )
        except (ValueError, TypeError, AttributeError):
            pass
        story.append(row_cards([
            metric('AI Risk Level', _text(getattr(analysis, 'level', None)).upper()),
            metric('AI Risk Score', _text(getattr(analysis, 'score', None))),
            metric('Relationship', comparison.relationship.replace('_', ' ') if comparison else 'Não disponível'),
            metric('Needs Attention', ('Yes' if comparison.needs_attention else 'No') if comparison else 'Não disponível'),
        ], [width / 4] * 4))
        story.append(Spacer(1, 6))
        story.append(para(f'Model: {_text(getattr(analysis, "model", None))}  |  '
                          f'Date (UTC): {_date(getattr(analysis, "created_at", None))}', 'small'))
        story.append(Spacer(1, 6))
        story.append(para('AI REASONS', 'label'))
        for reason in _parsed_reasons(getattr(analysis, 'reasons', None)):
            t = Table([[para(reason)]], colWidths=[width])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), PALE),
                ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.extend([t, Spacer(1, 5)])

    section('Human Review History')
    if not reviews:
        story.append(para('Não existem revisões humanas registadas.'))
    for idx, review in enumerate(reviews or [], 1):
        story.append(card(f'Review {idx}', [
            ('Reviewer', getattr(review, 'reviewer', None)),
            ('Decision', getattr(review, 'decision', None)),
            ('Previous status', getattr(review, 'previous_status', None)),
            ('New status', getattr(review, 'new_status', None)),
            ('Notes', getattr(review, 'notes', None)),
            ('Review date (UTC)', _date(getattr(review, 'created_at', None))),
        ]))
        story.append(Spacer(1, 8))

    section('Case Action History')
    if not actions:
        story.append(para('Não existem ações registadas.'))
    for idx, action in enumerate(actions or [], 1):
        story.append(card(f'Action {idx}', [
            ('Action type', getattr(action, 'action_type', None)),
            ('Status', getattr(action, 'status', None)),
            ('Notes', getattr(action, 'notes', None)),
            ('Destination', getattr(action, 'destination', None)),
            ('Platform', getattr(action, 'platform', None)),
            ('External reference', getattr(action, 'external_reference', None)),
            ('External result', getattr(action, 'external_result', None)),
            ('Created (UTC)', _date(getattr(action, 'created_at', None))),
            ('Submitted (UTC)', _date(getattr(action, 'submitted_at', None))),
            ('Responded (UTC)', _date(getattr(action, 'responded_at', None))),
        ]))
        story.append(Spacer(1, 8))

    section('Evidence Metadata')
    story.append(para('Esta secção apresenta apenas os metadados das evidências registadas. '
                      'Não inclui fotografias, vídeos ou ficheiros originais.', 'small'))
    if not evidences:
        story.append(para('Não existem evidências associadas registadas.'))
    for idx, evidence in enumerate(evidences or [], 1):
        story.append(card(f'Evidence {idx}', [
            ('Evidence ID', getattr(evidence, 'id', None)),
            ('Evidence type', getattr(evidence, 'evidence_type', None)),
            ('Platform', getattr(evidence, 'platform', None)),
            ('Source URL', getattr(evidence, 'source_url', None)),
            ('External reference', getattr(evidence, 'external_reference', None)),
            ('Content hash', getattr(evidence, 'content_hash', None)),
            ('Notes', getattr(evidence, 'notes', None)),
            ('Captured (UTC)', _date(getattr(evidence, 'captured_at', None))),
        ]))
        story.append(Spacer(1, 8))

    def decorate_page(pdf, doc):
        page_w, page_h = A4
        pdf.saveState()
        pdf.setFont('Helvetica-Bold', 9)
        pdf.setFillColor(colors.HexColor('#A00000'))
        pdf.drawRightString(page_w - 38, page_h - 26, 'CONFIDENCIAL')
        pdf.setStrokeColor(BORDER)
        pdf.line(38, 45, page_w - 38, 45)
        pdf.setFillColor(DARK)
        pdf.setFont('Helvetica', 8)
        pdf.drawString(38, 30, 'ChildSafe - Proteção de Crianças')
        pdf.drawRightString(page_w - 38, 30, f'Página {doc.page}')
        pdf.restoreState()

    document.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)
    buffer.seek(0)
    return buffer
