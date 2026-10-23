import json
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    HRFlowable,
)


LOGO_PATH = (
    Path(__file__).resolve().parents[1]
    / "static"
    / "brand"
    / "childsafe-logo.png"
)


def generate_report_pdf(report, ai_analyses=None, reviews=None, actions=None, evidences=None):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=55,
        title=f"ChildSafe - Denúncia CV-{report.id:06d}",
        author="ChildSafe",
    )

    styles = {
        "title": ParagraphStyle(
            "ChildSafeTitle",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            spaceAfter=8,
        ),
        "heading": ParagraphStyle(
            "ChildSafeHeading",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            spaceBefore=12,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "ChildSafeBody",
            fontName="Helvetica",
            fontSize=9,
            leading=14,
            spaceAfter=8,
            splitLongWords=True,
        ),
    }

    story = []

    # Logótipo oficial, mantendo as proporções
    story.append(
        Image(
            str(LOGO_PATH),
            width=150,
            height=50,
            hAlign="LEFT",
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "CHILDSAFE — RELATÓRIO DE DENÚNCIA",
            styles["title"],
        )
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#D9E2E8"),
        )
    )

    story.append(Spacer(1, 15))

    def add_field(label, value):
        text = (
            str(value)
            if value is not None and str(value).strip()
            else "Não fornecido"
        )

        story.append(
            Paragraph(
                escape(label),
                styles["heading"],
            )
        )

        story.append(
            Paragraph(
                escape(text).replace("\n", "<br/>"),
                styles["body"],
            )
        )

    add_field("Referência", f"CV-{report.id:06d}")

    date_text = (
        report.created_at.strftime("%d/%m/%Y %H:%M")
        if report.created_at
        else None
    )

    add_field("Data da denúncia (UTC)", date_text)
    add_field("Estado", report.status)
    add_field("Estado da revisão", report.review_status)
    add_field("Plataforma", report.platform)
    add_field("Motivo", report.reason)

    # URL original da publicação denunciada
    url = str(report.url or "").strip()
    parsed = urlparse(url)

    story.append(
        Paragraph(
            "Link da publicação denunciada",
            styles["heading"],
        )
    )

    if (
        parsed.scheme in {"http", "https"}
        and parsed.netloc
    ):
        safe_url = escape(url, {'"': "&quot;"})

        story.append(
            Paragraph(
                f'<link href="{safe_url}" color="blue">'
                f'{escape(url)}</link>',
                styles["body"],
            )
        )
    else:
        story.append(
            Paragraph(
                escape(url or "Não fornecido"),
                styles["body"],
            )
        )

    add_field(
        "Descrição original da denúncia",
        report.description,
    )
        # Localização geográfica do incidente
    story.append(
        Paragraph(
            "LOCALIZAÇÃO GEOGRÁFICA DO INCIDENTE",
            styles["title"],
        )
    )

    add_field(
        "Localização indicada na denúncia",
        getattr(report, "incident_location", None),
    )

    add_field(
        "Localização fornecida pelo denunciante",
        getattr(report, "reporter_location", None),
    )

    add_field(
        "Latitude",
        getattr(report, "geo_latitude", None),
    )

    add_field(
        "Longitude",
        getattr(report, "geo_longitude", None),
    )

    add_field(
        "Localização por extenso",
        getattr(report, "geo_location_text", None),
    )

    add_field(
        "Origem da informação geográfica",
        getattr(report, "geo_source", None),
    )

    add_field(
        "Estado de verificação geográfica",
        getattr(report, "geo_verification_status", None),
    )
        # Aviso de segurança geográfica
    story.append(
        Paragraph(
            "AVISO: As referências geográficas identificadas "
            "automaticamente são indícios preliminares. "
            "A menção de uma cidade, ilha ou instituição "
            "não confirma que o incidente tenha ocorrido "
            "nesse local. As coordenadas, quando disponíveis, "
            "devem ser interpretadas de acordo com a sua "
            "origem e sujeitas a verificação humana.",
            styles["body"],
        )
    )

    # Histórico de avaliações automáticas
    story.append(
        Paragraph(
            "AVALIAÇÕES AUTOMÁTICAS DE RISCO",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "Estas avaliações foram produzidas automaticamente. "
            "São indicadores preliminares de risco, não constituem "
            "prova de abuso e não substituem a análise humana.",
            styles["body"],
        )
    )

    analyses = ai_analyses or []

    if not analyses:
        add_field(
            "Histórico da IA",
            "Não existem avaliações automáticas registadas.",
        )

    for analysis in analyses:
        add_field("Modelo utilizado", analysis.model)
        add_field("Nível de risco", analysis.level)
        add_field("Pontuação", analysis.score)

        analysis_date = (
            analysis.created_at.strftime("%d/%m/%Y %H:%M")
            if analysis.created_at
            else None
        )
        add_field("Data da análise (UTC)", analysis_date)

        try:
            reasons = json.loads(analysis.reasons or "[]")
        except (json.JSONDecodeError, TypeError):
            reasons = analysis.reasons

        if isinstance(reasons, list):
            reasons_text = "\\n".join(str(item) for item in reasons)
        else:
            reasons_text = str(reasons or "Não fornecidos")

        add_field("Motivos identificados pela IA", reasons_text)

        story.append(Spacer(1, 10))


    # Histórico das revisões humanas
    story.append(
        Paragraph(
            "HISTÓRICO DE REVISÃO HUMANA",
            styles["title"],
        )
    )

    review_history = reviews or []

    if not review_history:
        add_field(
            "Revisões",
            "Não existem revisões humanas registadas.",
        )

    for review in review_history:
        add_field("Revisor", review.reviewer)
        add_field("Decisão", review.decision)
        add_field("Estado anterior", review.previous_status)
        add_field("Novo estado", review.new_status)
        add_field("Observações", review.notes)

        review_date = (
            review.created_at.strftime("%d/%m/%Y %H:%M")
            if review.created_at
            else None
        )

        add_field("Data da revisão (UTC)", review_date)
        story.append(Spacer(1, 10))


    # Histórico das ações registadas
    story.append(
        Paragraph(
            "HISTÓRICO DE AÇÕES",
            styles["title"],
        )
    )

    action_history = actions or []

    if not action_history:
        add_field(
            "Ações",
            "Não existem ações registadas.",
        )

    for action in action_history:
        add_field("Tipo de ação", action.action_type)
        add_field("Estado da ação", action.status)
        add_field("Observações", action.notes)
        add_field("Destino", action.destination)
        add_field("Plataforma", action.platform)
        add_field("Referência externa", action.external_reference)
        add_field("Resultado externo registado", action.external_result)

        for label, date_value in [
            ("Data de criação (UTC)", action.created_at),
            ("Data de envio registada (UTC)", action.submitted_at),
            ("Data de resposta registada (UTC)", action.responded_at),
        ]:
            formatted_date = (
                date_value.strftime("%d/%m/%Y %H:%M")
                if date_value
                else None
            )
            add_field(label, formatted_date)

        story.append(Spacer(1, 10))


    # Referências das evidências associadas
    story.append(
        Paragraph(
            "EVIDÊNCIAS ASSOCIADAS À DENÚNCIA",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "Esta secção apresenta apenas os metadados "
            "das evidências registadas. Não inclui "
            "fotografias, vídeos ou ficheiros originais.",
            styles["body"],
        )
    )

    evidence_history = evidences or []

    if not evidence_history:
        add_field(
            "Evidências",
            "Não existem evidências associadas registadas.",
        )

    for evidence in evidence_history:
        add_field("Identificador da evidência", evidence.id)
        add_field("Tipo de evidência", evidence.evidence_type)
        add_field("Plataforma", evidence.platform)
        add_field("URL de origem", evidence.source_url)
        add_field("Referência externa", evidence.external_reference)
        add_field("Hash de integridade registado", evidence.content_hash)
        add_field("Observações", evidence.notes)

        captured_date = (
            evidence.captured_at.strftime("%d/%m/%Y %H:%M")
            if evidence.captured_at
            else None
        )

        add_field("Data de recolha (UTC)", captured_date)

        story.append(Spacer(1, 10))

    # Cabeçalho e rodapé em todas as páginas
    def decorate_page(pdf, doc):
        width, height = A4

        pdf.saveState()

        pdf.setFont("Helvetica-Bold", 9)
        pdf.setFillColor(colors.HexColor("#A00000"))

        pdf.drawRightString(
            width - 45,
            height - 25,
            "CONFIDENCIAL",
        )

        pdf.setStrokeColor(colors.HexColor("#D9E2E8"))
        pdf.line(45, 45, width - 45, 45)

        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica", 8)

        pdf.drawString(
            45,
            30,
            "ChildSafe - Proteção de Crianças",
        )

        pdf.drawRightString(
            width - 45,
            30,
            f"Página {doc.page}",
        )

        pdf.restoreState()

    document.build(
        story,
        onFirstPage=decorate_page,
        onLaterPages=decorate_page,
    )

    buffer.seek(0)
    return buffer
