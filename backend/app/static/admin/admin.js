const loginView = document.getElementById("login-view");
const dashboardView = document.getElementById("dashboard-view");

const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

const logoutButton = document.getElementById("logout-button");
const periodFilter = document.getElementById("period-filter");
const dashboardSectionSelect =document.getElementById("dashboard-section-select");

let accessToken = sessionStorage.getItem("childsafe_access_token");
let currentUser = null;
let selectedReportId = null;
let cachedReports = [];
let activeReportFilter = "all";



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

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getNumericReportId(reportId) {
    const match = String(reportId).match(/^CV-(\d+)$/);

    if (!match) {
        throw new Error(
            `Invalid report ID: ${reportId}`
        );
    }

    return Number(match[1]);
}
function getAllowedNextStatuses(currentStatus) {
    const transitions = {
        pending: [
            "under_review",
        ],

        under_review: [
            "reviewed",
        ],

        reviewed: [
            "confirmed",
            "dismissed",
            "escalated",
        ],

        confirmed: [],
        dismissed: [],
        escalated: [],
    };

    return transitions[currentStatus] || [];
}
function updateStatusOptions(currentStatus) {
    const select = document.getElementById(
        "review-new-status"
    );

    const allowedStatuses =
        getAllowedNextStatuses(currentStatus);

    select.innerHTML = "";

    if (!allowedStatuses.length) {
        const option = document.createElement(
            "option"
        );

        option.value = "";
        option.textContent = "No further action";

        select.appendChild(option);
        select.disabled = true;

        return;
    }

    select.disabled = false;

    const placeholder = document.createElement(
        "option"
    );

    placeholder.value = "";
    placeholder.textContent = "Select status";
    placeholder.disabled = true;
    placeholder.selected = true;

    select.appendChild(placeholder);

    allowedStatuses.forEach(status => {
        const option = document.createElement(
            "option"
        );

        option.value = status;

        option.textContent = status
            .replaceAll("_", " ")
            .replace(/\b\w/g, letter =>
                letter.toUpperCase()
            );

        select.appendChild(option);
    });
}
async function openReport(reportId) {
    selectedReportId = reportId;
    const numericReportId =
    getNumericReportId(reportId);

    console.log(
        "Opening report:",
        reportId
    );

    const panel = document.getElementById(
        "report-review-panel"
    );

    const response = await apiFetch(
        `/reports/${numericReportId}/audit`
    );

    if (!response.ok) {
        const errorText = await response.text();

        console.error(
            "Unable to load report audit:",
            response.status,
            errorText
        );

        throw new Error(
            `Unable to load report ${reportId}.`
        );
    }

    const data = await response.json();

    console.log(
        "Report audit loaded:",
        data
    );

    document.getElementById(
        "selected-report-id"
    ).textContent = reportId;

    document.getElementById(
        "review-platform"
    ).textContent = (
        data.report?.platform || "—"
    );
   
    document.getElementById(
        "review-risk-level"
    ).textContent = (
        data.deterministic_assessment?.level || "—"
    );

    const riskLevel = (
        data.deterministic_assessment?.level
        || "unknown"
    );
    
    const riskElement = document.getElementById(
        "review-risk-level"
    );
    
    riskElement.textContent = riskLevel
        .replaceAll("_", " ")
        .toUpperCase();
    
    riskElement.className = (
        `status-badge risk-${riskLevel}`
    );
    
    document.getElementById(
        "review-risk-score"
    ).textContent = (
        data.deterministic_assessment?.score
        ?? "—"
    );
   
    
    const currentStatus = (
        data.review?.current_status || "unknown"
    );
   

    const statusElement = document.getElementById(
        "review-current-status"
    );
    
    statusElement.textContent = currentStatus
        .replaceAll("_", " ")
        .toUpperCase();
    
    statusElement.className = (
        `status-badge status-${currentStatus}`
    );
    document.getElementById(
        "review-source-type"
    ).textContent = (
        data.report?.source_type
            ?.replaceAll("_", " ")
            || "Unknown"
    );
    
    document.getElementById(
        "review-source-channel"
    ).textContent = (
        data.report?.source_channel
            ?.replaceAll("_", " ")
            || "—"
    );
    document.getElementById(
        "review-source-reference"
    ).textContent = (
        data.report?.source_reference
        || "—"
    );
    const detectionSection = document.getElementById(
        "automated-detection-section"
    );
    
    const detection = data.detection || {};
    
    if (
        data.report?.source_type === "automated_monitoring"
        && detection.confidence !== null
        && detection.confidence !== undefined
    ) {
        detectionSection.classList.remove(
            "hidden"
        );
    
        document.getElementById(
            "review-detection-confidence"
        ).textContent = (
            `${Math.round(
                detection.confidence * 100
            )}%`
        );
    
        document.getElementById(
            "review-detection-source"
        ).textContent = (
            detection.source || "—"
        );
    
        const signalsContainer =
            document.getElementById(
                "review-detection-signals"
            );
    
        const signals = Array.isArray(
            detection.signals
        )
            ? detection.signals
            : [];
    
        if (!signals.length) {
            signalsContainer.innerHTML = `
                <span class="detection-empty">
                    No detection signals available.
                </span>
            `;
        } else {
            signalsContainer.innerHTML = signals
                .map(signal => `
                    <span class="detection-chip">
                        ${escapeHtml(
                            signal.replaceAll(
                                "_",
                                " "
                            )
                        )}
                    </span>
                `)
                .join("");
        }
    
    } else {
        detectionSection.classList.add(
            "hidden"
        );
    }
    const aiAssessment = data.ai_assessment || {};

document.getElementById(
    "review-ai-level"
).textContent = (
    aiAssessment.level
        ? aiAssessment.level.toUpperCase()
        : "UNAVAILABLE"
);

document.getElementById(
    "review-ai-score"
).textContent = (
    aiAssessment.score ?? "—"
);

const aiReasonsContainer = document.getElementById(
    "review-ai-reasons"
);

const aiReasons = Array.isArray(
    aiAssessment.reasons
)
    ? aiAssessment.reasons
    : [];

if (!aiReasons.length) {
    aiReasonsContainer.innerHTML = `
        <span class="detection-empty">
            No AI reasons available.
        </span>
    `;
} else {
    aiReasonsContainer.innerHTML = aiReasons
        .map(reason => `
            <div class="ai-reason-item">
                ${escapeHtml(reason)}
            </div>
        `)
        .join("");
}


        const comparison = data.risk_comparison || {};

        document.getElementById(
            "review-risk-relationship"
        ).textContent = (
            comparison.relationship
                ?.replaceAll("_", " ")
                || "—"
        );

        document.getElementById(
            "review-risk-attention"
        ).textContent = (
            comparison.needs_attention === true
                ? "Yes"
                : comparison.needs_attention === false
                    ? "No"
                    : "—"
        );
    document.getElementById(
        "review-reason"
    ).textContent = (
        data.report?.reason || "—"
    );

    document.getElementById(
        "review-description"
    ).textContent = (
        data.report?.description || "—"
    );

    const reportUrl = document.getElementById(
        "review-url"
    );

    if (data.report?.url) {
        reportUrl.href = data.report.url;
        reportUrl.textContent = "Open reported content";
    } else {
        reportUrl.href = "#";
        reportUrl.textContent = "No URL available";
    }

    renderTable(
        "report-review-history",
        [
            {
                key: "previous_status",
                label: "Previous",
            },
            {
                key: "new_status",
                label: "New status",
            },
            {
                key: "decision",
                label: "Decision",
            },
            {
                key: "reviewer",
                label: "Reviewer",
            },
            {
                key: "created_at",
                label: "Created",
            },
        ],
        data.review?.history || [],
    );

    document.getElementById(
        "review-form"
    ).reset();

    updateStatusOptions(currentStatus);
    
    document.getElementById(
        "review-message"
    ).textContent = "";

    panel.classList.remove("hidden");

    panel.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}

async function submitReview(
    reportId,
    newStatus,
    decision,
    notes,
) {
    const numericReportId =
    getNumericReportId(reportId);
    const response = await apiFetch(
        `/reports/${numericReportId}/review`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                new_status: newStatus,
                decision,
                notes,
            }),
        },
    );

    if (!response.ok) {
        const errorData = await response.json();

        const detail = errorData.detail;

        if (typeof detail === "string") {
            throw new Error(detail);
        }

        if (detail?.error) {
            throw new Error(detail.error);
        }

        throw new Error(
            "Unable to submit review."
        );
    }

    return response.json();
}


async function loadReportHistory(reportId) {
    const numericReportId =
        getNumericReportId(reportId);

    const response = await apiFetch(
        `/reports/${numericReportId}/reviews`
    );

    // restante código igual

    if (!response.ok) {
        return;
    }

    const rows = await response.json();

    renderTable(
        "report-review-history",
        [
            {
                key: "previous_status",
                label: "Previous",
            },
            {
                key: "new_status",
                label: "New status",
            },
            {
                key: "decision",
                label: "Decision",
            },
            {
                key: "reviewer",
                label: "Reviewer",
            },
            {
                key: "created_at",
                label: "Created",
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
        console.error(
            "Unable to load review queue:",
            response.status
        );
        return;
    }

    const rows = await response.json();

    const urgentRows = rows.filter(
        row => row.queue_priority === "urgent"
    );

    const container = document.getElementById(
        "review-queue"
    );

    if (!urgentRows.length) {
        container.innerHTML = `
            <div class="empty-state">
                No urgent reports awaiting review.
            </div>
        `;
        return;
    }

    const rowsHtml = urgentRows
        .map(row => `
            <tr
                class="review-queue-row"
                data-report-id="${escapeHtml(row.report_id)}"
            >
                <td>
                    <button
                        type="button"
                        class="report-link"
                        data-report-id="${escapeHtml(row.report_id)}"
                    >
                        ${escapeHtml(row.report_id)}
                    </button>
                </td>

                <td>${escapeHtml(row.platform)}</td>
              
                <td>
                    ${escapeHtml(
                        (
                            row.source_type
                            || "unknown"
                        ).replaceAll("_", " ")
                    )}
                </td>

                <td>${escapeHtml(row.risk_level)}</td>


                <td>${escapeHtml(row.risk_score)}</td>

                <td>
                    ${escapeHtml(
                        row.queue_priority_reason
                    )}
                </td>

                <td>
                    ${escapeHtml(row.created_at)}
                </td>
            </tr>
        `)
        .join("");

    container.innerHTML = `
        <table>
            <thead>
            <tr>
                <th>Report</th>
                <th>Platform</th>
                <th>Source</th>
                <th>Risk</th>
                <th>Score</th>
                <th>Priority reason</th>
                <th>Created</th>
             </tr>
            </thead>

            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
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
        loadMonitoringRuns(),
        loadRecentReports(),
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

async function loadMonitoringRuns() {
    const response = await apiFetch(
        "/monitoring/runs?limit=10"
    );

    if (!response.ok) {
        console.error(
            "Unable to load monitoring runs:",
            response.status
        );
        return;
    }

    const runs = await response.json();

    const lastRun = runs[0];

    if (lastRun) {
        document.getElementById(
            "monitoring-last-run"
        ).textContent = (
            `#${lastRun.run_id}`
        );

        document.getElementById(
            "monitoring-status"
        ).textContent = (
            lastRun.status || "—"
        );

        document.getElementById(
            "monitoring-platform"
        ).textContent = (
            lastRun.platform || "—"
        );

        document.getElementById(
            "monitoring-candidates"
        ).textContent = (
            lastRun.candidates_found ?? 0
        );

        document.getElementById(
            "monitoring-relevant"
        ).textContent = (
            lastRun.candidates_relevant ?? 0
        );

        document.getElementById(
            "monitoring-ignored"
        ).textContent = (
            lastRun.candidates_ignored ?? 0
        );

        document.getElementById(
            "monitoring-created"
        ).textContent = (
            lastRun.reports_created ?? 0
        );

        document.getElementById(
            "monitoring-duplicates"
        ).textContent = (
            lastRun.duplicates_skipped ?? 0
        );

        document.getElementById(
            "monitoring-errors"
        ).textContent = (
            lastRun.errors_count ?? 0
        );
    }

    renderTable(
        "monitoring-runs",
        [
            {
                key: "run_id",
                label: "Run",
            },
            {
                key: "platform",
                label: "Platform",
            },
            {
                key: "status",
                label: "Status",
            },
            {
                key: "candidates_found",
                label: "Found",
            },
            {
                key: "candidates_relevant",
                label: "Relevant",
            },
            {
                key: "candidates_ignored",
                label: "Ignored",
            },
            {
                key: "reports_created",
                label: "Created",
            },
            {
                key: "duplicates_skipped",
                label: "Duplicates",
            },
            {
                key: "errors_count",
                label: "Errors",
            },
            {
                key: "started_at",
                label: "Started",
            },
        ],
        runs,
    );
}
function renderRecentReportsTable(reports) {
    const container = document.getElementById(
        "recent-reports"
    );

    const rows = reports.slice(0, 100);

    if (!rows.length) {
        container.innerHTML = `
            <div class="empty-state">
                No reports found.
            </div>
        `;

        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Report</th>
                    <th>Platform</th>
                    <th>Source</th>
                    <th>Risk</th>
                    <th>Score</th>
                    <th>Review status</th>
                    <th>Created</th>
                </tr>
            </thead>

            <tbody>
                ${rows.map(report => {
                    const source = (
                        report.source_type
                        || "unknown"
                    ).replaceAll("_", " ");

                    const status = (
                        report.review_status
                        || "unknown"
                    ).replaceAll("_", " ");

                    return `
                        <tr>
                            <td>
                                <button
                                    type="button"
                                    class="report-link recent-report-link"
                                    data-report-id="${escapeHtml(
                                        report.report_id
                                    )}"
                                >
                                    ${escapeHtml(
                                        report.report_id
                                    )}
                                </button>
                            </td>

                            <td>
                                ${escapeHtml(
                                    report.platform || "—"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(source)}
                            </td>

                            <td>
                                ${escapeHtml(
                                    report.risk_level || "—"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    String(
                                        report.risk_score ?? "—"
                                    )
                                )}
                            </td>

                            <td>
                                ${escapeHtml(status)}
                            </td>

                            <td>
                                ${escapeHtml(
                                    report.created_at || "—"
                                )}
                            </td>
                        </tr>
                    `;
                }).join("")}
            </tbody>
        </table>
    `;
}
async function loadRecentReports() {
    const response = await apiFetch(
        "/reports/"
    );

    if (!response.ok) {
        console.error(
            "Unable to load recent reports:",
            response.status
        );

        return;
    }

    cachedReports = await response.json();

    if (
        dashboardSectionSelect.value
        === "recent-reports"
    ) {
        renderRecentReportsTable(
            cachedReports
        );
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
function applyReportFilter(filter) {
    activeReportFilter = filter;

    if (filter === "urgent") {
        dashboardSectionSelect.value =
            "urgent-queue";

        showDashboardSection(
            "urgent-queue"
        );

        loadReviewQueue();
        return;
    }

    let reports = cachedReports;

    if (filter === "pending") {
        reports = cachedReports.filter(
            report =>
                report.review_status === "pending"
        );
    }

    if (filter === "confirmed") {
        reports = cachedReports.filter(
            report =>
                report.review_status === "confirmed"
        );
    }

    if (filter === "escalated") {
        reports = cachedReports.filter(
            report =>
                report.review_status === "escalated"
        );
    }

    dashboardSectionSelect.value =
        "recent-reports";

    showDashboardSection(
        "recent-reports"
    );

    renderRecentReportsTable(
        reports
    );
}
logoutButton.addEventListener(
    "click",
    logout,
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

document.getElementById(
    "close-report-button"
).addEventListener(
    "click",
    () => {
        selectedReportId = null;

        document.getElementById(
            "report-review-panel"
        ).classList.add("hidden");
    },
);


document
    .getElementById("review-queue")
    .addEventListener(
        "click",
        async event => {
            const button = event.target.closest(
                ".report-link"
            );

            if (!button) {
                return;
            }

            const reportId =
                button.dataset.reportId;

            console.log(
                "Report clicked:",
                reportId
            );

            try {
                await openReport(reportId);
            } catch (error) {
                console.error(
                    "Unable to open report:",
                    error
                );
            }
        },
    );
    document
    .getElementById("recent-reports")
    .addEventListener(
        "click",
        async event => {
            const button = event.target.closest(
                ".recent-report-link"
            );

            if (!button) {
                return;
            }

            const reportId =
                button.dataset.reportId;

            console.log(
                "Recent report clicked:",
                reportId
            );

            try {
                await openReport(
                    reportId
                );
            } catch (error) {
                console.error(
                    "Unable to open recent report:",
                    error
                );
            }
        },
    );
   
    function showDashboardSection(section) {
        const sections = {
           
            monitoring:
                document.getElementById(
                    "monitoring-section"
                ),
    
            "report-trend":
                document.getElementById(
                    "report-trend-section"
                ),
    
            "review-trend":
                document.getElementById(
                    "review-trend-section"
                ),
    
            "urgent-queue":
                document.getElementById(
                    "urgent-queue-section"
                ),
    
            "recent-reports":
                document.getElementById(
                    "recent-reports-section"
                ),
    
            reviewers:
                document.getElementById(
                    "reviewers-panel"
                ),
    
            audit:
                document.getElementById(
                    "audit-panel"
                ),
        };
    
        Object.values(sections).forEach(
            element => {
                if (element) {
                    element.classList.add(
                        "hidden"
                    );
                }
            }
        );
    
        const selected =
            sections[section];
    
        if (selected) {
            selected.classList.remove(
                "hidden"
            );
        }
    }
document.getElementById(
    "review-form"
).addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        if (!selectedReportId) {
            return;
        }

        const message = document.getElementById(
            "review-message"
        );

        message.textContent = "";

        const newStatus = document.getElementById(
            "review-new-status"
        ).value;

        const decision = document.getElementById(
            "review-decision"
        ).value.trim();

        const notes = document.getElementById(
            "review-notes"
        ).value.trim();

        try {
            await submitReview(
                selectedReportId,
                newStatus,
                decision,
                notes,
            );

            message.textContent = (
                "Review submitted successfully."
            );

            await Promise.all([
                openReport(selectedReportId),
                loadReviewQueue(),
                loadMetrics(),
                loadReviewTrend(),
                loadAuditLog(),
            ]);

        } catch (error) {
            message.textContent = error.message;
        }
    },

);


dashboardSectionSelect.addEventListener(
    "change",
    async () => {
        const section =
            dashboardSectionSelect.value;

        if (section === "monitoring") {
            await loadMonitoringRuns();
        }

        if (section === "urgent-queue") {
            await loadReviewQueue();
        }

        if (section === "recent-reports") {
            await loadRecentReports();
        }

        if (section === "reviewers") {
            await loadReviewers();
        }

        if (section === "audit") {
            await loadAuditLog();
        }

        showDashboardSection(section);
    }
);
if (accessToken) {
    showDashboard();
}
document.addEventListener(
    "click",
    event => {
        const card = event.target.closest(
            ".metric-filter"
        );

        if (!card) {
            return;
        }

        const filter =
            card.dataset.reportFilter;

        applyReportFilter(filter);
    }
);