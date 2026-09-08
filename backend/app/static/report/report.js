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

    /* ========================================================
       PORTUGUÊS
       ======================================================== */

    pt: {
        pageTitle:
            "ChildSafe | Proteção Digital Infantil",

        navParents:
            "Para pais",

        navHelp:
            "Ajuda",

        navReport:
            "Denunciar",

        publicReporting:
            "Proteção infantil online",

        heroTitle:
            "Ajude a proteger uma criança online",

        heroText:
            "Denuncie conteúdo público na internet que possa expor, identificar ou colocar uma criança em risco.",

        openReportButton:
            "Fazer uma denúncia",

        heroSafeChildren:
            "Crianças seguras.",

        heroBrightFuture:
            "Futuros mais brilhantes.",


        learnEyebrow:
            "Informação e prevenção",

        learnTitle:
            "Proteja as crianças dentro e fora da internet",


        parentsTitle:
            "Proteja a privacidade das crianças",

        parentsIntro:
            "Uma fotografia pode revelar muito mais do que parece. Imagens, uniformes, escolas, locais frequentados e hábitos podem ajudar desconhecidos a identificar ou localizar uma criança.",


        childrenInternetTitle:
            "Ensine a criança a usar a internet com segurança",

        childrenInternetIntro:
            "Fale desde cedo sobre mensagens privadas, pedidos de segredo, partilha de fotografias, localização e contacto com desconhecidos. A educação digital começa em casa.",


        visitorsTitle:
            "Crianças não são atrações turísticas",

        visitorsIntro:
            "Ser turista, voluntário, visitante ou membro de uma organização não dá automaticamente o direito de fotografar, filmar ou publicar imagens de crianças.",


        reportEyebrow:
            "Denúncia",

        reportTitle:
            "Denuncie conteúdo online preocupante",


        anonymousTitle:
            "Pode denunciar anonimamente",

        anonymousText:
            "Não pedimos o seu nome nem email. Envie apenas o link público e a informação necessária para explicar a sua preocupação.",


        benefitAnonymous:
            "Pode denunciar anonimamente",

        benefitNoDownload:
            "Não descarregue nem partilhe imagens",

        benefitTogether:
            "Juntos por crianças mais seguras",


        impactTitle:
            "A sua denúncia faz a diferença",

        impactText:
            "Ao denunciar conteúdos preocupantes, contribui para um ambiente online mais seguro e ajuda a proteger crianças.",

        impactAnalyzedTitle:
            "Conteúdos analisados",

        impactAnalyzedText:
            "por equipas especializadas",

        impactRemovalTitle:
            "Ajuda a remover conteúdos",

        impactRemovalText:
            "nocivos da internet",

        impactProtectTitle:
            "Protege crianças",

        impactProtectText:
            "e constrói um futuro mais seguro",

        impactNote:
            "Mais segurança para um amanhã melhor.",


        helpTitle:
            "Precisa de ajuda agora?",

        complaintLine:
            "Disque Denúncia",

        pjTitle:
            "Polícia Judiciária",

        emergencyPraia:
            "Emergência",


        footerDescription:
            "Proteção digital infantil e segurança online.",

        footerInfo:
            "Informação",

        footerProtection:
            "Proteção",

        footerPolice:
            "Polícia Judiciária · 134",

        footerCountry:
            "ChildSafe · Cabo Verde",

        footerSlogan:
            "Crianças seguras. Futuros mais brilhantes. ♡",


        protectWhileReportingTitle:
            "Proteja a criança durante a denúncia",

        protectWhileReportingText:
            "Não descarregue, copie nem volte a publicar imagens ou vídeos da criança. Envie apenas o link original do conteúdo público.",


        platformLabel:
            "Plataforma",

        selectPlatform:
            "Selecione a plataforma",

        otherPlatform:
            "Outra",


        reasonLabel:
            "Por que está preocupado?",

        selectReason:
            "Selecione um motivo",

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

        descriptionLabel:
            "O que observou?",

        descriptionPlaceholder:
            "Descreva o que viu e por que considera preocupante.",


        submitButton:
            "Enviar denúncia",

        submitting:
            "A enviar...",

        success:
            "Denúncia enviada com sucesso. Referência: ",

        tooMany:
            "Foram enviadas demasiadas denúncias. Aguarde um momento e tente novamente.",

        unableSubmit:
            "Não foi possível enviar a denúncia.",
    },



    /* ========================================================
       ESPAÑOL
       ======================================================== */

    es: {
        pageTitle:
            "ChildSafe | Protección Digital Infantil",

        navParents:
            "Para padres",

        navHelp:
            "Ayuda",

        navReport:
            "Denunciar",

        publicReporting:
            "Protección infantil en línea",

        heroTitle:
            "Ayude a proteger a un niño en línea",

        heroText:
            "Denuncie contenido público en internet que pueda exponer, identificar o poner en riesgo a un niño.",

        openReportButton:
            "Hacer una denuncia",

        heroSafeChildren:
            "Niños seguros.",

        heroBrightFuture:
            "Futuros más brillantes.",


        learnEyebrow:
            "Información y prevención",

        learnTitle:
            "Proteja a los niños dentro y fuera de internet",


        parentsTitle:
            "Proteja la privacidad de los niños",

        parentsIntro:
            "Una fotografía puede revelar mucho más de lo que parece. Imágenes, uniformes, escuelas, lugares frecuentes y hábitos pueden ayudar a desconocidos a identificar o localizar a un niño.",


        childrenInternetTitle:
            "Enseñe al niño a usar internet de forma segura",

        childrenInternetIntro:
            "Hable desde pequeños sobre mensajes privados, secretos, fotografías, ubicación y contacto con desconocidos. La educación digital comienza en casa.",


        visitorsTitle:
            "Los niños no son atracciones turísticas",

        visitorsIntro:
            "Ser turista, voluntario, visitante o miembro de una organización no da automáticamente el derecho de fotografiar, grabar o publicar imágenes de niños.",


        reportEyebrow:
            "Denuncia",

        reportTitle:
            "Denuncie contenido preocupante en línea",


        anonymousTitle:
            "Puede denunciar de forma anónima",

        anonymousText:
            "No pedimos su nombre ni correo electrónico. Envíe solo el enlace público y la información necesaria para explicar su preocupación.",


        benefitAnonymous:
            "Puede denunciar de forma anónima",

        benefitNoDownload:
            "No descargue ni comparta imágenes",

        benefitTogether:
            "Juntos por niños más seguros",


        impactTitle:
            "Su denuncia marca la diferencia",

        impactText:
            "Al denunciar contenido preocupante, contribuye a crear un entorno digital más seguro y ayuda a proteger a los niños.",

        impactAnalyzedTitle:
            "Contenido analizado",

        impactAnalyzedText:
            "por equipos especializados",

        impactRemovalTitle:
            "Ayuda a eliminar contenido",

        impactRemovalText:
            "perjudicial de internet",

        impactProtectTitle:
            "Protege a los niños",

        impactProtectText:
            "y construye un futuro más seguro",

        impactNote:
            "Más seguridad para un mañana mejor.",


        helpTitle:
            "¿Necesita ayuda ahora?",

        complaintLine:
            "Línea de denuncia",

        pjTitle:
            "Policía Judicial",

        emergencyPraia:
            "Emergencia",


        footerDescription:
            "Protección digital infantil y seguridad en línea.",

        footerInfo:
            "Información",

        footerProtection:
            "Protección",

        footerPolice:
            "Policía Judicial · 134",

        footerCountry:
            "ChildSafe · Cabo Verde",

        footerSlogan:
            "Niños seguros. Futuros más brillantes. ♡",


        protectWhileReportingTitle:
            "Proteja al niño durante la denuncia",

        protectWhileReportingText:
            "No descargue, copie ni vuelva a publicar imágenes o vídeos del niño. Envíe únicamente el enlace original del contenido público.",


        platformLabel:
            "Plataforma",

        selectPlatform:
            "Seleccione la plataforma",

        otherPlatform:
            "Otra",


        reasonLabel:
            "¿Por qué le preocupa?",

        selectReason:
            "Seleccione un motivo",

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

        descriptionLabel:
            "¿Qué observó?",

        descriptionPlaceholder:
            "Describa lo que vio y por qué le preocupa.",


        submitButton:
            "Enviar denuncia",

        submitting:
            "Enviando...",

        success:
            "Denuncia enviada correctamente. Referencia: ",

        tooMany:
            "Se han enviado demasiadas denuncias. Espere un momento e inténtelo de nuevo.",

        unableSubmit:
            "No se pudo enviar la denuncia.",
    },



    /* ========================================================
       ENGLISH
       ======================================================== */

    en: {
        pageTitle:
            "ChildSafe | Digital Child Protection",

        navParents:
            "For parents",

        navHelp:
            "Help",

        navReport:
            "Report",

        publicReporting:
            "Online child protection",

        heroTitle:
            "Help protect a child online",

        heroText:
            "Report public online content that may expose, identify or endanger a child.",

        openReportButton:
            "Submit a report",

        heroSafeChildren:
            "Safe children.",

        heroBrightFuture:
            "Brighter futures.",


        learnEyebrow:
            "Information and prevention",

        learnTitle:
            "Protect children online and offline",


        parentsTitle:
            "Protect children's privacy",

        parentsIntro:
            "A photograph can reveal much more than it seems. Images, uniforms, schools, frequent locations and routines can help strangers identify or locate a child.",


        childrenInternetTitle:
            "Teach children to use the internet safely",

        childrenInternetIntro:
            "Talk early about private messages, requests for secrecy, sharing photos, location and contact with strangers. Digital safety education starts at home.",


        visitorsTitle:
            "Children are not tourist attractions",

        visitorsIntro:
            "Being a tourist, volunteer, visitor or organization member does not automatically give anyone the right to photograph, film or publish images of children.",


        reportEyebrow:
            "Report",

        reportTitle:
            "Report concerning online content",


        anonymousTitle:
            "You can report anonymously",

        anonymousText:
            "We do not ask for your name or email. Submit only the public link and the information needed to explain your concern.",


        benefitAnonymous:
            "You can report anonymously",

        benefitNoDownload:
            "Do not download or share images",

        benefitTogether:
            "Together for safer children",


        impactTitle:
            "Your report makes a difference",

        impactText:
            "By reporting concerning content, you help create a safer online environment and protect children.",

        impactAnalyzedTitle:
            "Content reviewed",

        impactAnalyzedText:
            "by specialized teams",

        impactRemovalTitle:
            "Helps remove harmful content",

        impactRemovalText:
            "from the internet",

        impactProtectTitle:
            "Protects children",

        impactProtectText:
            "and builds a safer future",

        impactNote:
            "More safety for a better tomorrow.",


        helpTitle:
            "Do you need help now?",

        complaintLine:
            "Reporting line",

        pjTitle:
            "Judicial Police",

        emergencyPraia:
            "Emergency",


        footerDescription:
            "Digital child protection and online safety.",

        footerInfo:
            "Information",

        footerProtection:
            "Protection",

        footerPolice:
            "Judicial Police · 134",

        footerCountry:
            "ChildSafe · Cabo Verde",

        footerSlogan:
            "Safe children. Brighter futures. ♡",


        protectWhileReportingTitle:
            "Protect the child while reporting",

        protectWhileReportingText:
            "Do not download, copy or republish images or videos of the child. Submit only the original public link.",


        platformLabel:
            "Platform",

        selectPlatform:
            "Select platform",

        otherPlatform:
            "Other",


        reasonLabel:
            "Why are you concerned?",

        selectReason:
            "Select a reason",

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

        descriptionLabel:
            "What did you notice?",

        descriptionPlaceholder:
            "Describe what you saw and why you are concerned.",


        submitButton:
            "Submit report",

        submitting:
            "Submitting...",

        success:
            "Report submitted successfully. Reference: ",

        tooMany:
            "Too many reports have been submitted. Please wait a moment and try again.",

        unableSubmit:
            "Unable to submit report.",
    },



    /* ========================================================
       FRANÇAIS
       ======================================================== */

    fr: {
        pageTitle:
            "ChildSafe | Protection Numérique des Enfants",

        navParents:
            "Pour les parents",

        navHelp:
            "Aide",

        navReport:
            "Signaler",

        publicReporting:
            "Protection des enfants en ligne",

        heroTitle:
            "Aidez à protéger un enfant en ligne",

        heroText:
            "Signalez tout contenu public en ligne susceptible d'exposer, d'identifier ou de mettre un enfant en danger.",

        openReportButton:
            "Faire un signalement",

        heroSafeChildren:
            "Des enfants en sécurité.",

        heroBrightFuture:
            "Des avenirs plus lumineux.",


        learnEyebrow:
            "Information et prévention",

        learnTitle:
            "Protégez les enfants en ligne et hors ligne",


        parentsTitle:
            "Protégez la vie privée des enfants",

        parentsIntro:
            "Une photographie peut révéler beaucoup plus qu'il n'y paraît. Les images, uniformes, écoles, lieux fréquentés et habitudes peuvent aider des inconnus à identifier ou localiser un enfant.",


        childrenInternetTitle:
            "Apprenez à l'enfant à utiliser internet en toute sécurité",

        childrenInternetIntro:
            "Parlez dès le plus jeune âge des messages privés, des demandes de secret, du partage de photos, de la localisation et des contacts avec des inconnus. L'éducation à la sécurité numérique commence à la maison.",


        visitorsTitle:
            "Les enfants ne sont pas des attractions touristiques",

        visitorsIntro:
            "Être touriste, bénévole, visiteur ou membre d'une organisation ne donne pas automatiquement le droit de photographier, filmer ou publier des images d'enfants.",


        reportEyebrow:
            "Signalement",

        reportTitle:
            "Signalez un contenu préoccupant en ligne",


        anonymousTitle:
            "Vous pouvez signaler anonymement",

        anonymousText:
            "Nous ne demandons ni votre nom ni votre adresse e-mail. Envoyez uniquement le lien public et les informations nécessaires pour expliquer votre inquiétude.",


        benefitAnonymous:
            "Vous pouvez signaler anonymement",

        benefitNoDownload:
            "Ne téléchargez ni ne partagez d'images",

        benefitTogether:
            "Ensemble pour des enfants plus en sécurité",


        impactTitle:
            "Votre signalement fait la différence",

        impactText:
            "En signalant des contenus préoccupants, vous contribuez à créer un environnement numérique plus sûr et à protéger les enfants.",

        impactAnalyzedTitle:
            "Contenus analysés",

        impactAnalyzedText:
            "par des équipes spécialisées",

        impactRemovalTitle:
            "Aide à supprimer les contenus",

        impactRemovalText:
            "nuisibles sur internet",

        impactProtectTitle:
            "Protège les enfants",

        impactProtectText:
            "et construit un avenir plus sûr",

        impactNote:
            "Plus de sécurité pour un avenir meilleur.",


        helpTitle:
            "Besoin d'aide maintenant ?",

        complaintLine:
            "Ligne de signalement",

        pjTitle:
            "Police Judiciaire",

        emergencyPraia:
            "Urgence",


        footerDescription:
            "Protection numérique des enfants et sécurité en ligne.",

        footerInfo:
            "Information",

        footerProtection:
            "Protection",

        footerPolice:
            "Police Judiciaire · 134",

        footerCountry:
            "ChildSafe · Cabo Verde",

        footerSlogan:
            "Des enfants en sécurité. Des avenirs plus lumineux. ♡",


        protectWhileReportingTitle:
            "Protégez l'enfant pendant le signalement",

        protectWhileReportingText:
            "Ne téléchargez, ne copiez et ne republiez pas les images ou vidéos de l'enfant. Envoyez uniquement le lien public original.",


        platformLabel:
            "Plateforme",

        selectPlatform:
            "Sélectionnez la plateforme",

        otherPlatform:
            "Autre",


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

        descriptionLabel:
            "Qu'avez-vous remarqué ?",

        descriptionPlaceholder:
            "Décrivez ce que vous avez vu et pourquoi cela vous inquiète.",


        submitButton:
            "Envoyer le signalement",

        submitting:
            "Envoi en cours...",

        success:
            "Signalement envoyé avec succès. Référence : ",

        tooMany:
            "Trop de signalements ont été envoyés. Veuillez patienter un moment puis réessayer.",

        unableSubmit:
            "Impossible d'envoyer le signalement.",
    },
};


/* ============================================================
   REPORT MODAL
   ============================================================ */

   const reportModal =
   document.getElementById(
       "report-modal"
   );

const closeReportModalButton =
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
   if (!reportModal) {
       console.error(
           "Report modal not found."
       );

       return;
   }

   reportModal.classList.remove(
       "hidden"
   );

   document.body.classList.add(
       "modal-open"
   );
}


function closeReportModalWindow() {
   if (!reportModal) {
       return;
   }

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


if (closeReportModalButton) {
   closeReportModalButton.addEventListener(
       "click",
       closeReportModalWindow
   );
}


if (reportModal) {
   const modalBackdrop =
       reportModal.querySelector(
           ".modal-backdrop"
       );

   if (modalBackdrop) {
       modalBackdrop.addEventListener(
           "click",
           closeReportModalWindow
       );
   }
}


document.addEventListener(
   "keydown",
   event => {
       if (
           event.key === "Escape"
           && reportModal
           && !reportModal.classList.contains(
               "hidden"
           )
       ) {
           closeReportModalWindow();
       }
   }
);

/* ============================================================
   TRANSLATION
   ============================================================ */

function translatePage(language) {
    const dictionary =
        translations[language]
        || translations.pt;

    currentLanguage = language;

    document.documentElement.lang =
        language;

    document.title =
        dictionary.pageTitle;


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



/* ============================================================
   PUBLIC REPORT SUBMISSION

   NÃO ALTERAR O CONTRATO COM O BACKEND:
   POST /reports/public

   JSON:
   - platform
   - url
   - reason
   - description
   ============================================================ */

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


            const responseText =
                await response.text();

            let data = {};

            try {
                data = responseText
                    ? JSON.parse(responseText)
                    : {};
            } catch {
                data = {
                    detail: responseText,
                };
            }

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