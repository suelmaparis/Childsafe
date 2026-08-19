const loginView = document.getElementById("login-view");
const dashboardView = document.getElementById("dashboard-view");

const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

const logoutButton = document.getElementById("logout-button");
const refreshButton = document.getElementById("refresh-button");
const periodFilter = document.getElementById("period-filter");

let accessToken = sessionStorage.getItem("childsafe_access_token");
let currentUser = null;


function authHeaders() {
    return {
        "Authorization": `Bearer ${accessToken}`,
    };
}


async function apiFetch(
    url,
    options = {},
) {
    const headers = {
        ...(options.headers || {}),
    };

    if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
    }

    const response = await fetch(
        url,
        {
            ...options,
            headers,
        },
    );

    if (response.status === 401) {
        logout();
        throw new Error("Authentication expired.");
    }

    return response;
}


function logout() {
    accessToken = null;
    currentUser = null;

    sessionStorage.removeItem(
        "childsafe_access_token"
    );

    dashboardView.classList.add("hidden");
    loginView.classList.remove("hidden");
}


async function login(
    username,
    password,
) {
    const body = new URLSearchParams();

    body.append("username", username);
    body.append("password", password);

    const response = await fetch(
        "/auth/login",
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },
            body,
        },
    );

    if (!response.ok) {
        throw new Error(
            "Incorrect username or password."
        );
    }

    const data = await response.json();

    accessToken = data.access_token;

    sessionStorage.setItem(
        "childsafe_access_token",
        accessToken,
    );
}


async function loadCurrentUser() {
    const response = await apiFetch(
        "/auth/me"
    );

    if (!response.ok) {
        throw new Error(
            "Unable to load reviewer."
        );
    }

    currentUser = await response.json();

    document.getElementById(
        "current-user"
    ).textContent = (
        `${currentUser.username} · ${currentUser.role}`
    );

    const isAdmin = (
        currentUser.role === "admin"
    );

    document.getElementById(
        "reviewers-panel"
    ).classList.toggle(
        "hidden",
        !isAdmin,
    );

    document.getElementById(
        "audit-panel"
    ).classList.toggle(
        "hidden",
        !isAdmin,
    );
}


async function loadMetrics() {
    const days = periodFilter.value;

    const response = await apiFetch(
        `/reports/admin/metrics?days=${days}`
    );

    if (!response.ok) {
        return;
    }

    const data = await response.json();

    document.getElementById(
        "metric-total"
    ).textContent = data.total_reports;

    document.getElementById(
        "metric-pending"
    ).textContent = data.pending;

    document.getElementById(
        "metric-urgent"
    ).textContent = data.urgent_pending;

    document.getElementById(
        "metric-confirmed"
    ).textContent = data.confirmed;

    document.getElementById(
        "metric-escalated"
    ).textContent = data.escalated;

    document.getElementById(
        "metric-confirmation-rate"
    ).textContent = (
        `${data.confirmation_rate}%`
    );

    document.getElementById(
        "risk-low"
    ).textContent = data.risk_distribution.low;

    document.getElementById(
        "risk-medium"
    ).textContent = data.risk_distribution.medium;

    document.getElementById(
        "risk-high"
    ).textContent = data.risk_distribution.high;

    document.getElementById(
        "risk-critical"
    ).textContent = data.risk_distribution.critical;
}


function renderTable(
    containerId,
    columns,
    rows,
) {
    const container = document.getElementById(
        containerId
    );

    if (!rows.length) {
        container.innerHTML = (
            `<div class="empty-state">
                No data available.
            </div>`
        );

        return;
    }

    const head = columns
        .map(
            column => `<th>${column.label}</th>`
        )
        .join("");

    const body = rows
        .map(row => {
            const cells = columns
                .map(column => {
                    const value = row[column.key];

                    return (
                        `<td>${value ?? ""}</td>`
                    );
                })
                .join("");

            return `<tr>${cells}</tr>`;
        })
        .join("");

    container.innerHTML = `
        <table>
            <thead>
                <tr>${head}</tr>
            </thead>

            <tbody>
                ${body}
            </tbody>
        </table>
    `;
}


async function loadReportTrend() {
    const days = periodFilter.value;

    const response = await apiFetch(
        `/reports/admin/metrics/trend?days=${days}`
    );

    if (!response.ok) {
        return;
    }

    const rows = await response.json();

    renderTable(
        "report-trend",
        [
            {
                key: "date",
                label: "Date",
            },
            {
                key: "created",
                label: "Created",
            },
            {
                key: "confirmed",
                label: "Confirmed",
            },
            {
                key: "escalated",
                label: "Escalated",
            },
        ],
        rows,
    );
}


async function loadReviewTrend() {
    const days = periodFilter.value;

    const response = await apiFetch(
        `/reports/admin/review-trend?days=${days}`
    );

    if (!response.ok) {
        return;
    }

    const rows = await response.json();

    renderTable(
        "review-trend",
        [
            {
                key: "date",
                label: "Date",
            },
            {
                key: "review_events",
                label: "Review events",
            },
            {
                key: "confirmed",
                label: "Confirmed",
            },
            {
                key: "dismissed",
                label: "Dismissed",
            },
            {
                key: "escalated",
                label: "Escalated",
            },
        ],
        rows,
    );
}


async function loadReviewQueue() {
    const response = await apiFetch(
        "/reports/review-queue"
    );

    if (!response.ok) {
        return;
    }

    const rows = await response.json();

    const urgentRows = rows.filter(
        row => row.queue_priority === "urgent"
    );

    renderTable(
        "review-queue",
        [
            {
                key: "report_id",
                label: "Report",
            },
            {
                key: "platform",
                label: "Platform",
            },
            {
                key: "risk_level",
                label: "Risk",
            },
            {
                key: "risk_score",
                label: "Score",
            },
            {
                key: "queue_priority_reason",
                label: "Priority reason",
            },
            {
                key: "created_at",
                label: "Created",
            },
        ],
        urgentRows,
    );
}


async function loadReviewers() {
    if (
        !currentUser
        || currentUser.role !== "admin"
    ) {
        return;
    }

    const response = await apiFetch(
        "/auth/reviewers"
    );

    if (!response.ok) {
        return;
    }

    const rows = await response.json();

    renderTable(
        "reviewers-list",
        [
            {
                key: "id",
                label: "ID",
            },
            {
                key: "username",
                label: "Username",
            },
            {
                key: "role",
                label: "Role",
            },
            {
                key: "is_active",
                label: "Active",
            },
            {
                key: "created_at",
                label: "Created",
            },
        ],
        rows,
    );
}


async function loadAuditLog() {
    if (
        !currentUser
        || currentUser.role !== "admin"
    ) {
        return;
    }

    const response = await apiFetch(
        "/auth/audit-logs?limit=50&offset=0"
    );

    if (!response.ok) {
        return;
    }

    const data = await response.json();

    renderTable(
        "audit-log",
        [
            {
                key: "id",
                label: "ID",
            },
            {
                key: "actor_reviewer_id",
                label: "Actor",
            },
            {
                key: "target_reviewer_id",
                label: "Target",
            },
            {
                key: "action",
                label: "Action",
            },
            {
                key: "details",
                label: "Details",
            },
            {
                key: "created_at",
                label: "Created",
            },
        ],
        data.items,
    );
}


async function loadDashboard() {
    await loadCurrentUser();

    await Promise.all([
        loadMetrics(),
        loadReportTrend(),
        loadReviewTrend(),
        loadReviewQueue(),
        loadReviewers(),
        loadAuditLog(),
    ]);
}


async function showDashboard() {
    loginView.classList.add("hidden");
    dashboardView.classList.remove("hidden");

    try {
        await loadDashboard();
    } catch (error) {
        console.error(error);
    }
}


loginForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        loginError.textContent = "";

        const username = document.getElementById(
            "username"
        ).value;

        const password = document.getElementById(
            "password"
        ).value;

        try {
            await login(
                username,
                password,
            );

            await showDashboard();

            loginForm.reset();

        } catch (error) {
            loginError.textContent = (
                error.message
            );
        }
    }
);


logoutButton.addEventListener(
    "click",
    logout,
);


refreshButton.addEventListener(
    "click",
    loadDashboard,
);


periodFilter.addEventListener(
    "change",
    async () => {
        await Promise.all([
            loadMetrics(),
            loadReportTrend(),
            loadReviewTrend(),
        ]);
    }
);


if (accessToken) {
    showDashboard();
}
