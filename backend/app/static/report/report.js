const form = document.getElementById(
    "public-report-form"
);

const submitButton = document.getElementById(
    "submit-button"
);

const formMessage = document.getElementById(
    "form-message"
);


form.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        formMessage.textContent = "";
        formMessage.className = "form-message";

        const platform = document.getElementById(
            "platform"
        ).value;

        const url = document.getElementById(
            "url"
        ).value.trim();

        const reason = document.getElementById(
            "reason"
        ).value;

        const description = document.getElementById(
            "description"
        ).value.trim();

        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";

        try {
            const response = await fetch(
                "/reports/public",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        platform,
                        url,
                        reason,
                        description,
                    }),
                },
            );

            const data = await response.json();

            if (!response.ok) {
                console.error(
                    "Report submission error:",
                    response.status,
                    data
                );
            
                if (
                    response.status === 422
                    && Array.isArray(data.detail)
                ) {
                    const messages = data.detail.map(
                        error => {
                            const field = (
                                error.loc?.[
                                    error.loc.length - 1
                                ] || "field"
                            );
            
                            return `${field}: ${error.msg}`;
                        }
                    );
            
                    throw new Error(
                        messages.join(" | ")
                    );
                }
            
                if (response.status === 429) {
                    throw new Error(
                        "Too many reports submitted. Please wait a moment and try again."
                    );
                }
            
                throw new Error(
                    "Unable to submit report."
                );
            }

            form.reset();

            formMessage.className = (
                "form-message success-message"
            );

            formMessage.textContent = (
                `Report submitted successfully. ` +
                `Reference: ${data.report_id}`
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
            submitButton.textContent = (
                "Submit report"
            );
        }
    },
);

