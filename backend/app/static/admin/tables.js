// CHILDSAFE CV — TABLE PRESENTATION
// Melhora apenas a apresentação das tabelas existentes.

(() => {
    "use strict";

    const RISK_CLASSES = [
        "risk-low",
        "risk-medium",
        "risk-high",
        "risk-critical"
    ];

    const STATUS_CLASSES = [
        "status-received",
        "status-pending",
        "status-under_review",
        "status-reviewed",
        "status-confirmed",
        "status-rejected",
        "status-escalated"
    ];

    function createBadge(cell, value, type) {
        const normalized = value
            .trim()
            .toLowerCase()
            .replaceAll(" ", "_");

        const className = `${type}-${normalized}`;

        const allowed = type === "risk"
            ? RISK_CLASSES
            : STATUS_CLASSES;

        if (!allowed.includes(className)) {
            return;
        }

        // Preservar o texto original.
        const badge = document.createElement("span");

        badge.className = `status-badge ${className}`;
        badge.textContent = value;

        cell.replaceChildren(badge);
    }

    function enhanceTable(table) {
        const headers = Array.from(
            table.querySelectorAll("thead th")
        ).map(header =>
            header.textContent.trim().toLowerCase()
        );

        const riskIndex = headers.findIndex(
            header => header === "risk"
        );

        const statusIndex = headers.findIndex(
            header =>
                header === "review status" ||
                header === "status"
        );

        table.querySelectorAll("tbody tr").forEach(row => {
            const cells = row.querySelectorAll("td");

            if (riskIndex >= 0 && cells[riskIndex]) {
                const cell = cells[riskIndex];

                if (!cell.querySelector(".status-badge")) {
                    createBadge(
                        cell,
                        cell.textContent,
                        "risk"
                    );
                }
            }

            if (statusIndex >= 0 && cells[statusIndex]) {
                const cell = cells[statusIndex];

                if (!cell.querySelector(".status-badge")) {
                    createBadge(
                        cell,
                        cell.textContent,
                        "status"
                    );
                }
            }
        });
    }

    function enhanceTables() {
        document.querySelectorAll(
            "#dashboard-view table"
        ).forEach(enhanceTable);
    }

    let scheduled = false;

    const observer = new MutationObserver(() => {
        if (scheduled) return;

        scheduled = true;

        requestAnimationFrame(() => {
            scheduled = false;
            enhanceTables();
        });
    });

    const dashboard = document.getElementById(
        "dashboard-view"
    );

    if (dashboard) {
        observer.observe(dashboard, {
            childList: true,
            subtree: true
        });

        enhanceTables();
    }
})();