const form = document.getElementById(
    "public-report-form"
);

const submitButton = document.getElementById(
    "submit-button"
);

const formMessage = document.getElementById(
    "form-message"
);

const languageSelect = document.getElementById(
    "language-select"
);

let currentLanguage = "pt";


const translations = {
    pt: {
        languageLabel: "Idioma",
        brandSubtitle: "Proteção Digital Infantil",
        publicReporting: "Denúncia Pública",
        heroTitle: "Ajude a proteger uma criança online",
        heroText:
            "Denuncie conteúdo público na internet que possa expor, identificar ou colocar uma criança em risco.",

        helpEyebrow: "Apoio e proteção",
        helpTitle: "Precisa de ajuda agora?",
        helpIntro:
            "Se uma criança estiver em perigo, for vítima de abuso, exploração, ameaça ou exposição grave, procure apoio imediatamente.",

        iccaDescription:
            "Instituto Cabo-verdiano da Criança e do Adolescente. Apoio, proteção e denúncia de situações que envolvam crianças e adolescentes.",
        complaintLine: "Disque Denúncia",
        centralServices: "Serviços Centrais",

        pjTitle: "Polícia Judiciária",
        pjDescription:
            "Contacte a Polícia Judiciária quando houver suspeita de crime, abuso, exploração sexual, ameaça ou outro perigo grave.",
        emergencyPraia: "Emergência",
        emergencyMindelo: "São Vicente",

        helpDisclaimer:
            "ChildSafe não substitui os serviços policiais, judiciais, médicos ou de proteção infantil. Em situações urgentes, contacte diretamente as autoridades.",

        parentsEyebrow: "Para pais e responsáveis",
        parentsTitle: "Proteja a privacidade das crianças",
        parentsIntro:
            "Uma fotografia pode revelar muito mais do que parece. Imagens, uniformes, escolas, locais frequentes e rotinas podem ajudar desconhecidos a identificar ou localizar uma criança.",

        sharingTitle: "Antes de publicar",
        sharing1:
            "Evite mostrar o nome completo, escola, uniforme ou endereço da criança.",
        sharing2:
            "Não publique rotinas, horários ou locais que a criança frequenta regularmente.",
        sharing3:
            "Verifique quem pode ver, guardar ou partilhar as fotografias.",
        sharing4:
            "Pense se a criança poderá sentir-se desconfortável com aquela imagem no futuro.",

        childrenInternetTitle:
            "Ensine a criança a usar a internet com segurança",
        childrenInternet1:
            "Explique que pessoas online podem não ser quem dizem ser.",
        childrenInternet2:
            "Ensine a nunca enviar fotografias, vídeos, morada, localização ou nome da escola a desconhecidos.",
        childrenInternet3:
            "Diga à criança que pode falar consigo sem medo se alguém online a fizer sentir desconfortável.",
        childrenInternet4:
            "Ensine que um adulto nunca deve pedir a uma criança para guardar conversas, fotografias ou encontros em segredo.",
        childrenInternet5:
            "Explique que deve bloquear e contar a um adulto de confiança quando alguém insistir, ameaçar ou pedir imagens.",

        visitorsEyebrow:
            "Turistas, visitantes e voluntários",
        visitorsTitle:
            "Crianças não são atrações turísticas",
        visitorsIntro:
            "Ser turista, voluntário, membro de uma organização ou visitante não dá a ninguém o direito automático de fotografar, filmar ou publicar uma criança.",

        photoConsentTitle:
            "Proteja o direito da criança à imagem",
        photoConsentText:
            "Pais, responsáveis, escolas, associações e instituições devem perguntar quem pretende fotografar a criança, porquê, onde a imagem será publicada e durante quanto tempo será utilizada.",

        visitorRule1:
            "Não aceite fotografias apenas porque a pessoa diz ser turista, voluntário, influenciador ou membro de uma ONG.",
        visitorRule2:
            "Pergunte para que finalidade a imagem será utilizada e em que plataforma será publicada.",
        visitorRule3:
            "Não permita imagens que exponham nudez, sofrimento, doença, pobreza, situações humilhantes ou momentos vulneráveis da criança.",
        visitorRule4:
            "Crianças devem poder dizer que não querem ser fotografadas.",
        visitorRule5:
            "Se uma fotografia ou vídeo de uma criança for publicado de forma preocupante, guarde o endereço da publicação e faça uma denúncia.",

        reportEyebrow: "Fazer uma denúncia",
        reportTitle:
            "Denuncie conteúdo online preocupante",

        anonymousTitle:
            "Pode denunciar anonimamente",
        anonymousText:
            "Não pedimos o seu nome nem email. Envie apenas o link público e a informação necessária para explicar a sua preocupação.",

        protectWhileReportingTitle:
            "Proteja a criança durante a denúncia",
        protectWhileReportingText:
            "Não descarregue, copie nem volte a publicar imagens ou vídeos da criança. Envie apenas o link original do conteúdo público.",

        immediateDangerTitle:
            "Perigo imediato?",
        immediateDangerText:
            "Se acredita que uma criança está em perigo físico imediato, contacte as autoridades competentes além de enviar esta denúncia.",

        reportDetailsTitle:
            "Detalhes da denúncia",
        reportDetailsText:
            "Diga-nos onde encontrou o conteúdo e por que acredita que pode colocar uma criança em risco.",

        platformLabel: "Plataforma",
        selectPlatform: "Selecione a plataforma",
        otherPlatform: "Outra",

        reasonLabel:
            "Por que está preocupado?",
        selectReason: "Selecione um motivo",
        reasonExposure:
            "Criança exposta publicamente",
        reasonLocation:
            "Localização, escola ou rotina revelada",
        reasonPrivacy:
            "Informação pessoal da criança exposta",
        reasonExploitation:
            "Possível exploração ou abuso",
        reasonSexualized:
            "Conteúdo sexualizado ou inadequado",
        reasonOther:
            "Outra preocupação relacionada com segurança infantil",

        urlLabel:
            "Link para o conteúdo público",
        urlHelp:
            "Cole o endereço original da publicação, fotografia ou vídeo.",

        descriptionLabel: "O que observou?",
        descriptionHelp:
            "Explique o que o preocupa. Não inclua informação pessoal desnecessária sobre a criança.",
        descriptionPlaceholder:
            "Descreva o que viu e por que considera preocupante.",
        characterLimit:
            "Máximo de 2.000 caracteres",

        submissionNote:
            "O ChildSafe irá avaliar a denúncia e poderá priorizá-la para revisão humana com base em indicadores de risco para a segurança infantil.",

        submitButton: "Enviar denúncia",
        submitting: "A enviar...",

        success:
            "Denúncia enviada com sucesso. Referência: ",

        tooMany:
            "Foram enviadas demasiadas denúncias. Aguarde um momento e tente novamente.",

        unableSubmit:
            "Não foi possível enviar a denúncia.",

        footerText:
            "ChildSafe · Proteção digital infantil e segurança online",
    },

    es: {
        languageLabel: "Idioma",
        brandSubtitle: "Protección Digital Infantil",
        publicReporting: "Denuncia Pública",
        heroTitle: "Ayude a proteger a un niño en línea",
        heroText:
            "Denuncie contenido público en internet que pueda exponer, identificar o poner en riesgo a un niño.",

        helpEyebrow: "Apoyo y protección",
        helpTitle: "¿Necesita ayuda ahora?",
        helpIntro:
            "Si un niño está en peligro o es víctima de abuso, explotación, amenazas o exposición grave, busque ayuda de inmediato.",

        iccaDescription:
            "Instituto Caboverdiano de la Infancia y la Adolescencia. Apoyo, protección y denuncia de situaciones que afecten a niños y adolescentes.",
        complaintLine: "Línea de denuncia",
        centralServices: "Servicios Centrales",

        pjTitle: "Policía Judicial",
        pjDescription:
            "Contacte con la Policía Judicial si sospecha de un delito, abuso, explotación sexual, amenazas u otro peligro grave.",
        emergencyPraia: "Emergencia",
        emergencyMindelo: "São Vicente",

        helpDisclaimer:
            "ChildSafe no sustituye a los servicios policiales, judiciales, médicos o de protección infantil. En situaciones urgentes, contacte directamente con las autoridades.",

        parentsEyebrow: "Para padres y responsables",
        parentsTitle:
            "Proteja la privacidad de los niños",
        parentsIntro:
            "Una fotografía puede revelar mucho más de lo que parece. Imágenes, uniformes, escuelas, lugares frecuentes y rutinas pueden ayudar a desconocidos a identificar o localizar a un niño.",

        sharingTitle: "Antes de publicar",
        sharing1:
            "Evite mostrar el nombre completo, la escuela, el uniforme o la dirección del niño.",
        sharing2:
            "No publique rutinas, horarios o lugares que el niño frecuente regularmente.",
        sharing3:
            "Compruebe quién puede ver, guardar o compartir las fotografías.",
        sharing4:
            "Piense si el niño podría sentirse incómodo con esa imagen en el futuro.",

        childrenInternetTitle:
            "Enseñe al niño a usar internet de forma segura",
        childrenInternet1:
            "Explique que las personas en línea pueden no ser quienes dicen ser.",
        childrenInternet2:
            "Enséñele a no enviar fotos, vídeos, dirección, ubicación o nombre de la escuela a desconocidos.",
        childrenInternet3:
            "Dígale que puede hablar con usted sin miedo si alguien en internet le hace sentir incómodo.",
        childrenInternet4:
            "Enséñele que un adulto nunca debe pedirle que mantenga conversaciones, fotos o encuentros en secreto.",
        childrenInternet5:
            "Explique que debe bloquear y contárselo a un adulto de confianza si alguien insiste, amenaza o pide imágenes.",

        visitorsEyebrow:
            "Turistas, visitantes y voluntarios",
        visitorsTitle:
            "Los niños no son atracciones turísticas",
        visitorsIntro:
            "Ser turista, voluntario, miembro de una organización o visitante no da derecho automático a fotografiar, grabar o publicar imágenes de un niño.",

        photoConsentTitle:
            "Proteja el derecho del niño a su imagen",
        photoConsentText:
            "Padres, responsables, escuelas, asociaciones e instituciones deben preguntar quién quiere fotografiar al niño, por qué, dónde se publicará la imagen y durante cuánto tiempo se utilizará.",

        visitorRule1:
            "No acepte fotografías solo porque la persona diga ser turista, voluntario, influencer o miembro de una ONG.",
        visitorRule2:
            "Pregunte con qué finalidad se utilizará la imagen y en qué plataforma se publicará.",
        visitorRule3:
            "No permita imágenes que expongan desnudez, sufrimiento, enfermedad, pobreza, situaciones humillantes o momentos vulnerables.",
        visitorRule4:
            "Los niños deben poder decir que no quieren ser fotografiados.",
        visitorRule5:
            "Si una foto o vídeo de un niño se publica de forma preocupante, guarde el enlace y haga una denuncia.",

        reportEyebrow: "Hacer una denuncia",
        reportTitle:
            "Denuncie contenido preocupante en línea",

        anonymousTitle:
            "Puede denunciar de forma anónima",
        anonymousText:
            "No pedimos su nombre ni correo electrónico. Envíe solo el enlace público y la información necesaria para explicar su preocupación.",

        protectWhileReportingTitle:
            "Proteja al niño durante la denuncia",
        protectWhileReportingText:
            "No descargue, copie ni vuelva a publicar imágenes o vídeos del niño. Envíe únicamente el enlace original del contenido público.",

        immediateDangerTitle:
            "¿Peligro inmediato?",
        immediateDangerText:
            "Si cree que un niño está en peligro físico inmediato, contacte con las autoridades competentes además de enviar esta denuncia.",

        reportDetailsTitle:
            "Detalles de la denuncia",
        reportDetailsText:
            "Indíquenos dónde encontró el contenido y por qué cree que puede poner a un niño en riesgo.",

        platformLabel: "Plataforma",
        selectPlatform: "Seleccione la plataforma",
        otherPlatform: "Otra",

        reasonLabel:
            "¿Por qué le preocupa?",
        selectReason: "Seleccione un motivo",
        reasonExposure:
            "Niño expuesto públicamente",
        reasonLocation:
            "Ubicación, escuela o rutina revelada",
        reasonPrivacy:
            "Información personal del niño expuesta",
        reasonExploitation:
            "Posible explotación o abuso",
        reasonSexualized:
            "Contenido sexualizado o inapropiado",
        reasonOther:
            "Otra preocupación de seguridad infantil",

        urlLabel:
            "Enlace al contenido público",
        urlHelp:
            "Pegue la URL original de la publicación, fotografía o vídeo.",

        descriptionLabel: "¿Qué observó?",
        descriptionHelp:
            "Explique qué le preocupa. No incluya información personal innecesaria sobre el niño.",
        descriptionPlaceholder:
            "Describa lo que vio y por qué le preocupa.",
        characterLimit:
            "Máximo 2.000 caracteres",

        submissionNote:
            "ChildSafe evaluará la denuncia y podrá priorizarla para revisión humana según indicadores de riesgo para la seguridad infantil.",

        submitButton: "Enviar denuncia",
        submitting: "Enviando...",

        success:
            "Denuncia enviada correctamente. Referencia: ",

        tooMany:
            "Se han enviado demasiadas denuncias. Espere un momento e inténtelo de nuevo.",

        unableSubmit:
            "No se pudo enviar la denuncia.",

        footerText:
            "ChildSafe · Protección digital infantil y seguridad en línea",
    },

    en: {
        languageLabel: "Language",
        brandSubtitle: "Digital Child Protection",
        publicReporting: "Public Reporting",
        heroTitle: "Help protect a child online",
        heroText:
            "Report public online content that may expose, identify or endanger a child.",

        helpEyebrow: "Support and protection",
        helpTitle: "Do you need help now?",
        helpIntro:
            "If a child is in danger or experiencing abuse, exploitation, threats or serious exposure, seek help immediately.",

        iccaDescription:
            "Cabo Verdean Institute for Children and Adolescents. Support, protection and reporting of situations involving children and adolescents.",
        complaintLine: "Reporting line",
        centralServices: "Central Services",

        pjTitle: "Judicial Police",
        pjDescription:
            "Contact the Judicial Police when you suspect a crime, abuse, sexual exploitation, threats or another serious danger.",
        emergencyPraia: "Emergency",
        emergencyMindelo: "São Vicente",

        helpDisclaimer:
            "ChildSafe does not replace police, judicial, medical or child-protection services. In urgent situations, contact the authorities directly.",

        parentsEyebrow: "For parents and caregivers",
        parentsTitle: "Protect children's privacy",
        parentsIntro:
            "A photograph can reveal much more than it seems. Images, uniforms, schools, frequent locations and routines can help strangers identify or locate a child.",

        sharingTitle: "Before posting",
        sharing1:
            "Avoid showing the child's full name, school, uniform or address.",
        sharing2:
            "Do not publish routines, schedules or places the child regularly visits.",
        sharing3:
            "Check who can view, save or share the photographs.",
        sharing4:
            "Consider whether the child may feel uncomfortable with the image in the future.",

        childrenInternetTitle:
            "Teach children to use the internet safely",
        childrenInternet1:
            "Explain that people online may not be who they claim to be.",
        childrenInternet2:
            "Teach them never to send photos, videos, home address, location or school name to strangers.",
        childrenInternet3:
            "Tell the child they can speak to you without fear if someone online makes them uncomfortable.",
        childrenInternet4:
            "Teach them that an adult should never ask a child to keep conversations, images or meetings secret.",
        childrenInternet5:
            "Explain that they should block the person and tell a trusted adult if someone pressures, threatens or asks for images.",

        visitorsEyebrow:
            "Tourists, visitors and volunteers",
        visitorsTitle:
            "Children are not tourist attractions",
        visitorsIntro:
            "Being a tourist, volunteer, organization member or visitor does not automatically give anyone the right to photograph, film or publish a child.",

        photoConsentTitle:
            "Protect the child's right to their image",
        photoConsentText:
            "Parents, caregivers, schools, associations and institutions should ask who wants to photograph the child, why, where the image will be published and how long it will be used.",

        visitorRule1:
            "Do not allow photographs simply because someone says they are a tourist, volunteer, influencer or NGO member.",
        visitorRule2:
            "Ask what the image will be used for and where it will be published.",
        visitorRule3:
            "Do not allow images that expose nudity, suffering, illness, poverty, humiliation or vulnerable moments.",
        visitorRule4:
            "Children should be able to say that they do not want to be photographed.",
        visitorRule5:
            "If a child's photo or video is published in a concerning way, save the link and submit a report.",

        reportEyebrow: "Submit a report",
        reportTitle:
            "Report concerning online content",

        anonymousTitle:
            "You can report anonymously",
        anonymousText:
            "We do not ask for your name or email. Submit only the public link and the information needed to explain your concern.",

        protectWhileReportingTitle:
            "Protect the child while reporting",
        protectWhileReportingText:
            "Do not download, copy or republish images or videos of the child. Submit only the original public link.",

        immediateDangerTitle:
            "Immediate danger?",
        immediateDangerText:
            "If you believe a child is in immediate physical danger, contact the appropriate authorities in addition to submitting this report.",

        reportDetailsTitle:
            "Report details",
        reportDetailsText:
            "Tell us where you found the content and why you believe it may put a child at risk.",

        platformLabel: "Platform",
        selectPlatform: "Select platform",
        otherPlatform: "Other",

        reasonLabel:
            "Why are you concerned?",
        selectReason: "Select a reason",
        reasonExposure:
            "Child shown or exposed publicly",
        reasonLocation:
            "Location, school or routine revealed",
        reasonPrivacy:
            "Child's personal information exposed",
        reasonExploitation:
            "Possible exploitation or abuse",
        reasonSexualized:
            "Sexualized or inappropriate content",
        reasonOther:
            "Other child-safety concern",

        urlLabel:
            "Link to the public content",
        urlHelp:
            "Paste the original post, photo or video URL.",

        descriptionLabel:
            "What did you notice?",
        descriptionHelp:
            "Describe what concerns you. Do not include unnecessary personal information about the child.",
        descriptionPlaceholder:
            "Describe what you saw and why you are concerned.",
        characterLimit:
            "Maximum 2,000 characters",

        submissionNote:
            "ChildSafe will assess the report and may prioritise it for human review based on child-safety risk indicators.",

        submitButton: "Submit report",
        submitting: "Submitting...",

        success:
            "Report submitted successfully. Reference: ",

        tooMany:
            "Too many reports have been submitted. Please wait a moment and try again.",

        unableSubmit:
            "Unable to submit report.",

        footerText:
            "ChildSafe · Digital child protection and online safety",
    },

    fr: {
        languageLabel: "Langue",
        brandSubtitle: "Protection Numérique des Enfants",
        publicReporting: "Signalement Public",
        heroTitle:
            "Aidez à protéger un enfant en ligne",
        heroText:
            "Signalez tout contenu public en ligne susceptible d'exposer, d'identifier ou de mettre un enfant en danger.",

        helpEyebrow: "Aide et protection",
        helpTitle:
            "Besoin d'aide maintenant ?",
        helpIntro:
            "Si un enfant est en danger ou victime d'abus, d'exploitation, de menaces ou d'une exposition grave, demandez de l'aide immédiatement.",

        iccaDescription:
            "Institut capverdien de l'Enfance et de l'Adolescence. Aide, protection et signalement de situations concernant les enfants et adolescents.",
        complaintLine: "Ligne de signalement",
        centralServices: "Services centraux",

        pjTitle: "Police Judiciaire",
        pjDescription:
            "Contactez la Police Judiciaire en cas de suspicion de crime, d'abus, d'exploitation sexuelle, de menace ou de danger grave.",
        emergencyPraia: "Urgence",
        emergencyMindelo: "São Vicente",

        helpDisclaimer:
            "ChildSafe ne remplace pas les services de police, de justice, de santé ou de protection de l'enfance. En cas d'urgence, contactez directement les autorités.",

        parentsEyebrow:
            "Pour les parents et responsables",
        parentsTitle:
            "Protégez la vie privée des enfants",
        parentsIntro:
            "Une photographie peut révéler beaucoup plus qu'il n'y paraît. Les images, uniformes, écoles, lieux fréquents et habitudes peuvent aider des inconnus à identifier ou localiser un enfant.",

        sharingTitle: "Avant de publier",
        sharing1:
            "Évitez d'afficher le nom complet, l'école, l'uniforme ou l'adresse de l'enfant.",
        sharing2:
            "Ne publiez pas les habitudes, horaires ou lieux que l'enfant fréquente régulièrement.",
        sharing3:
            "Vérifiez qui peut voir, enregistrer ou partager les photographies.",
        sharing4:
            "Demandez-vous si l'enfant pourrait être gêné par cette image à l'avenir.",

        childrenInternetTitle:
            "Apprenez à l'enfant à utiliser internet en toute sécurité",
        childrenInternet1:
            "Expliquez que les personnes en ligne ne sont pas toujours celles qu'elles prétendent être.",
        childrenInternet2:
            "Apprenez-lui à ne jamais envoyer de photos, vidéos, adresse, localisation ou nom de l'école à des inconnus.",
        childrenInternet3:
            "Dites à l'enfant qu'il peut vous parler sans crainte si quelqu'un en ligne le met mal à l'aise.",
        childrenInternet4:
            "Apprenez-lui qu'un adulte ne doit jamais demander à un enfant de garder secrètes des conversations, des images ou des rencontres.",
        childrenInternet5:
            "Expliquez qu'il faut bloquer la personne et prévenir un adulte de confiance si quelqu'un insiste, menace ou demande des images.",

        visitorsEyebrow:
            "Touristes, visiteurs et bénévoles",
        visitorsTitle:
            "Les enfants ne sont pas des attractions touristiques",
        visitorsIntro:
            "Être touriste, bénévole, membre d'une organisation ou visiteur ne donne pas automatiquement le droit de photographier, filmer ou publier un enfant.",

        photoConsentTitle:
            "Protégez le droit de l'enfant à son image",
        photoConsentText:
            "Les parents, responsables, écoles, associations et institutions doivent demander qui souhaite photographier l'enfant, pourquoi, où l'image sera publiée et pendant combien de temps elle sera utilisée.",

        visitorRule1:
            "N'acceptez pas les photographies uniquement parce que la personne affirme être touriste, bénévole, influenceur ou membre d'une ONG.",
        visitorRule2:
            "Demandez à quoi l'image servira et sur quelle plateforme elle sera publiée.",
        visitorRule3:
            "N'autorisez pas les images exposant la nudité, la souffrance, la maladie, la pauvreté, l'humiliation ou des moments de vulnérabilité.",
        visitorRule4:
            "Les enfants doivent pouvoir dire qu'ils ne veulent pas être photographiés.",
        visitorRule5:
            "Si une photo ou une vidéo d'un enfant est publiée de manière préoccupante, conservez le lien et faites un signalement.",

        reportEyebrow: "Faire un signalement",
        reportTitle:
            "Signalez un contenu préoccupant en ligne",

        anonymousTitle:
            "Vous pouvez signaler anonymement",
        anonymousText:
            "Nous ne demandons ni votre nom ni votre adresse e-mail. Envoyez uniquement le lien public et les informations nécessaires pour expliquer votre inquiétude.",

        protectWhileReportingTitle:
            "Protégez l'enfant pendant le signalement",
        protectWhileReportingText:
            "Ne téléchargez, ne copiez et ne republiez pas les images ou vidéos de l'enfant. Envoyez uniquement le lien public original.",

        immediateDangerTitle:
            "Danger immédiat ?",
        immediateDangerText:
            "Si vous pensez qu'un enfant est en danger physique immédiat, contactez les autorités compétentes en plus d'envoyer ce signalement.",

        reportDetailsTitle:
            "Détails du signalement",
        reportDetailsText:
            "Indiquez-nous où vous avez trouvé le contenu et pourquoi vous pensez qu'il peut mettre un enfant en danger.",

        platformLabel: "Plateforme",
        selectPlatform:
            "Sélectionnez la plateforme",
        otherPlatform: "Autre",

        reasonLabel:
            "Pourquoi êtes-vous inquiet ?",
        selectReason:
            "Sélectionnez un motif",
        reasonExposure:
            "Enfant exposé publiquement",
        reasonLocation:
            "Lieu, école ou habitudes révélés",
        reasonPrivacy:
            "Informations personnelles de l'enfant exposées",
        reasonExploitation:
            "Exploitation ou abus possible",
        reasonSexualized:
            "Contenu sexualisé ou inapproprié",
        reasonOther:
            "Autre préoccupation liée à la sécurité des enfants",

        urlLabel:
            "Lien vers le contenu public",
        urlHelp:
            "Collez l'URL originale de la publication, photo ou vidéo.",

        descriptionLabel:
            "Qu'avez-vous remarqué ?",
        descriptionHelp:
            "Décrivez ce qui vous inquiète. N'incluez pas d'informations personnelles inutiles concernant l'enfant.",
        descriptionPlaceholder:
            "Décrivez ce que vous avez vu et pourquoi cela vous inquiète.",
        characterLimit:
            "Maximum 2 000 caractères",

        submissionNote:
            "ChildSafe évaluera le signalement et pourra le prioriser pour un examen humain selon les indicateurs de risque pour la sécurité des enfants.",

        submitButton: "Envoyer le signalement",
        submitting: "Envoi en cours...",

        success:
            "Signalement envoyé avec succès. Référence : ",

        tooMany:
            "Trop de signalements ont été envoyés. Veuillez patienter un moment puis réessayer.",

        unableSubmit:
            "Impossible d'envoyer le signalement.",

        footerText:
            "ChildSafe · Protection numérique des enfants et sécurité en ligne",
    },
};

const reportModal =
    document.getElementById(
        "report-modal"
    );

const closeReportModal =
    document.getElementById(
        "close-report-modal"
    );

const reportButtons = [
    document.getElementById(
        "header-report-button"
    ),
    document.getElementById(
        "hero-report-button"
    ),
    document.getElementById(
        "cta-report-button"
    ),
    document.getElementById(
        "footer-report-button"
    ),
];


function openReportModal() {
    reportModal.classList.remove(
        "hidden"
    );

    document.body.classList.add(
        "modal-open"
    );
}


function closeReportModalWindow() {
    reportModal.classList.add(
        "hidden"
    );

    document.body.classList.remove(
        "modal-open"
    );
}


reportButtons.forEach(button => {
    if (!button) {
        return;
    }

    button.addEventListener(
        "click",
        openReportModal
    );
});


closeReportModal.addEventListener(
    "click",
    closeReportModalWindow
);


reportModal
    .querySelector(
        ".modal-backdrop"
    )
    .addEventListener(
        "click",
        closeReportModalWindow
    );


document.addEventListener(
    "keydown",
    event => {
        if (
            event.key === "Escape"
            && !reportModal.classList.contains(
                "hidden"
            )
        ) {
            closeReportModalWindow();
        }
    }
);
function translatePage(language) {
    const dictionary =
        translations[language]
        || translations.pt;

    currentLanguage = language;

    document.documentElement.lang =
        language;

    document.querySelectorAll(
        "[data-i18n]"
    ).forEach(element => {
        const key =
            element.dataset.i18n;

        if (
            dictionary[key]
            !== undefined
        ) {
            element.textContent =
                dictionary[key];
        }
    });

    document.querySelectorAll(
        "[data-i18n-placeholder]"
    ).forEach(element => {
        const key =
            element.dataset.i18nPlaceholder;

        if (
            dictionary[key]
            !== undefined
        ) {
            element.placeholder =
                dictionary[key];
        }
    });
}


languageSelect.addEventListener(
    "change",
    event => {
        translatePage(
            event.target.value
        );
    }
);


translatePage("pt");


form.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        formMessage.textContent = "";
        formMessage.className =
            "form-message";

        const dictionary =
            translations[currentLanguage];

        const platform =
            document.getElementById(
                "platform"
            ).value;

        const url =
            document.getElementById(
                "url"
            ).value.trim();

        const reason =
            document.getElementById(
                "reason"
            ).value;

        const description =
            document.getElementById(
                "description"
            ).value.trim();

        submitButton.disabled = true;

        submitButton.textContent =
            dictionary.submitting;

        try {
            const response = await fetch(
                "/reports/public",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        platform,
                        url,
                        reason,
                        description,
                    }),
                },
            );

            const data =
                await response.json();

            if (!response.ok) {
                console.error(
                    "Report submission error:",
                    response.status,
                    data
                );

                if (
                    response.status === 422
                    && Array.isArray(
                        data.detail
                    )
                ) {
                    const messages =
                        data.detail.map(
                            error => {
                                const field = (
                                    error.loc?.[
                                        error.loc.length - 1
                                    ]
                                    || "field"
                                );

                                return (
                                    `${field}: `
                                    + error.msg
                                );
                            }
                        );

                    throw new Error(
                        messages.join(" | ")
                    );
                }

                if (
                    response.status === 429
                ) {
                    throw new Error(
                        dictionary.tooMany
                    );
                }

                throw new Error(
                    dictionary.unableSubmit
                );
            }

            form.reset();

            formMessage.className = (
                "form-message success-message"
            );

            formMessage.textContent = (
                dictionary.success
                + data.report_id
            );

        } catch (error) {
            console.error(
                "Public report submission failed:",
                error
            );

            formMessage.className = (
                "form-message error-message"
            );

            formMessage.textContent =
                error.message;

        } finally {
            submitButton.disabled = false;

            submitButton.textContent =
                dictionary.submitButton;
        }
    },
);

