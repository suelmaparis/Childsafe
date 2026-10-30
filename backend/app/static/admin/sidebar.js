// CHILDSAFE CV — SIDEBAR NAVIGATION
// Reutiliza a navegação existente sem modificar admin.js.

(() => {
    const select = document.getElementById(
        "dashboard-section-select"
    );

    const navigation = document.getElementById(
        "sidebar-navigation"
    );

    const sidebarFooter = document.querySelector(
        "#admin-sidebar .sidebar-footer"
    );

    const logoutButton = document.getElementById(
        "logout-button"
    );

    if (!select || !navigation) {
        return;
    }

    // Transferir o botão original para a barra lateral.
    if (sidebarFooter && logoutButton) {
        sidebarFooter.appendChild(logoutButton);
    }

    function renderNavigation() {
        navigation.replaceChildren();

        const options = Array.from(select.options);

        options.forEach(option => {
            if (
                option.disabled ||
                option.hidden ||
                !option.value
            ) {
                return;
            }

            const button = document.createElement("button");

            button.type = "button";
            button.className = "sidebar-link";
            button.textContent = option.textContent.trim();
            button.dataset.section = option.value;

            const isActive = select.value === option.value;

            button.classList.toggle("active", isActive);

            if (isActive) {
                button.setAttribute("aria-current", "page");
            }

            button.addEventListener("click", () => {
                if (option.disabled || option.hidden) {
                    return;
                }

                select.value = option.value;

                select.dispatchEvent(
                    new Event("change", {
                        bubbles: true
                    })
                );

                updateActive();
            });

            navigation.appendChild(button);
        });
    }

    function updateActive() {
        navigation.querySelectorAll(".sidebar-link")
            .forEach(button => {
                const active =
                    button.dataset.section === select.value;

                button.classList.toggle("active", active);

                if (active) {
                    button.setAttribute(
                        "aria-current",
                        "page"
                    );
                } else {
                    button.removeAttribute("aria-current");
                }
            });
    }

    select.addEventListener("change", updateActive);

    // Aguarda que o admin.js carregue o utilizador e
    // atualize as opções permitidas.
    const observer = new MutationObserver(renderNavigation);

    observer.observe(select, {
        subtree: true,
        attributes: true,
        attributeFilter: ["hidden", "disabled"]
    });

    renderNavigation();

    // Atualiza também quando o login terminar.
    const dashboard = document.getElementById("dashboard-view");

    if (dashboard) {
        const dashboardObserver = new MutationObserver(() => {
            if (!dashboard.classList.contains("hidden")) {
                renderNavigation();
            }
        });

        dashboardObserver.observe(dashboard, {
            attributes: true,
            attributeFilter: ["class"]
        });
    }
    // CHILDSAFE CV — LIVE CONFIRMATION DONUT

const confirmationValue = document.getElementById(
    "metric-confirmation-rate"
);

const confirmationDonut = document.getElementById(
    "confirmation-donut"
);

if (confirmationValue && confirmationDonut) {

    function updateConfirmationDonut() {
        const rawValue = confirmationValue.textContent.trim();

        const parsed = Number.parseFloat(
            rawValue.replace("%", "").replace(",", ".")
        );

        const percentage = Number.isFinite(parsed)
            ? Math.min(100, Math.max(0, parsed))
            : 0;

        confirmationDonut.style.setProperty(
            "--confirmation-percent",
            `${percentage}%`
        );
    }

    const confirmationObserver = new MutationObserver(
        updateConfirmationDonut
    );

    confirmationObserver.observe(confirmationValue, {
        childList: true,
        characterData: true,
        subtree: true
    });

    updateConfirmationDonut();
}
// CHILDSAFE CV — LIVE RISK DISTRIBUTION BARS

const riskLevels = [
    { id: "risk-low", className: "risk-low-fill" },
    { id: "risk-medium", className: "risk-medium-fill" },
    { id: "risk-high", className: "risk-high-fill" },
    { id: "risk-critical", className: "risk-critical-fill" }
];

const riskItems = riskLevels.map(level => {
    const valueElement = document.getElementById(level.id);

    if (!valueElement) return null;

    const row = valueElement.closest(".risk-row");

    if (!row) return null;

    const track = document.createElement("div");
    track.className = "risk-track";

    const fill = document.createElement("div");
    fill.className = `risk-fill ${level.className}`;

    track.appendChild(fill);
    row.insertBefore(track, valueElement);

    return { valueElement, fill };
}).filter(Boolean);

function updateRiskBars() {
    const values = riskItems.map(item => {
        const value = Number(item.valueElement.textContent.trim());
        return Number.isFinite(value) ? Math.max(0, value) : 0;
    });

    const total = values.reduce((sum, value) => sum + value, 0);

    riskItems.forEach((item, index) => {
        const percentage = total > 0
            ? (values[index] / total) * 100
            : 0;

        item.fill.style.width = `${percentage}%`;
    });
}

riskItems.forEach(item => {
    const observer = new MutationObserver(updateRiskBars);

    observer.observe(item.valueElement, {
        childList: true,
        characterData: true,
        subtree: true
    });
});

updateRiskBars();

// CHILDSAFE CV — OVERVIEW LAYOUT

function organizeOverview() {
    const dashboard = document.querySelector(
        "#dashboard-view .dashboard"
    );

    const metricsGrid = dashboard?.querySelector(
        ".metrics-grid"
    );

    const confirmationCard = document.querySelector(
        ".confirmation-card"
    );

    const riskSection = document.getElementById(
        "risk-distribution-section"
    );

    const overviewSection = document.getElementById(
        "overview-section"
    );

    const alertsGrid = document.querySelector(
        ".review-alert-metrics"
    );

    const alertsPanel = alertsGrid?.closest(".panel");

    if (
        !dashboard ||
        !metricsGrid ||
        !confirmationCard ||
        !riskSection ||
        !overviewSection ||
        !alertsPanel
    ) {
        return;
    }

    // Evitar criar o layout mais de uma vez.
    if (document.getElementById("overview-panels")) {
        return;
    }

    const panels = document.createElement("div");
    panels.id = "overview-panels";
    panels.className = "overview-panels";

    // Criar o painel do gráfico circular.
    const confirmationPanel = document.createElement("section");
    confirmationPanel.className = "panel confirmation-panel admin-only";

    const confirmationHeader = document.createElement("div");
    confirmationHeader.className = "panel-header";

    const confirmationTitle = document.createElement("h2");
    confirmationTitle.textContent = "Confirmation rate";

    confirmationHeader.appendChild(confirmationTitle);
    confirmationPanel.appendChild(confirmationHeader);

    // Preservar o cartão e o ID original.
    confirmationPanel.appendChild(confirmationCard);

    // Colocar os três painéis na mesma linha.
    panels.appendChild(confirmationPanel);
    panels.appendChild(riskSection);
    panels.appendChild(alertsPanel);

    // Manter os painéis dentro do Overview.
    overviewSection.appendChild(panels);

    // Posicionar o Overview imediatamente após os indicadores.
    metricsGrid.insertAdjacentElement(
        "afterend",
        overviewSection
    );
}

organizeOverview();
})();

/* ChildSafeCV — Topbar date and time */
(function () {
    function setupTopbarClock() {
        const dateElement = document.getElementById("topbar-date");
        const timeElement = document.getElementById("topbar-time");

        if (!dateElement || !timeElement) return;

        function updateClock() {
            const now = new Date();

            dateElement.textContent = now.toLocaleDateString("pt-PT", {
                day: "numeric",
                month: "long",
                year: "numeric"
            });

            timeElement.textContent = now.toLocaleTimeString("pt-PT", {
                hour: "2-digit",
                minute: "2-digit"
            });
        }

        updateClock();
        setInterval(updateClock, 60000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", setupTopbarClock);
    } else {
        setupTopbarClock();
    }
})();
