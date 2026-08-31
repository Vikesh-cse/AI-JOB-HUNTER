import time
from datetime import datetime
import streamlit as st

try:
    from agents import workflow
except ImportError:
    from agents import workflow

from database import (
    create_table,
    get_applications,
    update_status,
    reject_application,
)

st.set_page_config(
    page_title="AI Job Hunter",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

create_table()

PAGES = ["Dashboard", "Find Jobs", "Applications", "Resume Analysis"]

STATUS_ORDER = [
    "Pending Approval",
    "Approved",
    "Applied",
    "Interview",
    "Rejected",
    "Hired",
]

APP_FIELDS = (
    "application_id",
    "company",
    "job_title",
    "location",
    "job_url",
    "ats_score",
    "status",
    "created_date",
    "approved_date",
    "applied_date",
    "interview_date",
    "last_updated",
    "notes",
    "rejection_reason",
)

def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --navy: #0B1F3A;
            --navy2: #132D52;
            --blue: #4F46E5;
            --blue2: #6366F1;
            --green: #16A34A;
            --amber: #D97706;
            --red: #DC2626;
            --purple: #7C3AED;
            --bg: #F6F8FC;
            --card: #FFFFFF;
            --text: #172033;
            --muted: #667085;
            --border: #E4E7EC;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        .stMarkdown, .stMarkdown p, .stMarkdown span,
        .stMarkdown div, label, [data-testid="stCaptionContainer"] {
            color: var(--text);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B1F3A 0%, #0D274A 100%);
        }

        section[data-testid="stSidebar"] * {
            color: #F5F7FB !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            border-radius: 12px;
            padding: 0.55rem 0.75rem;
            margin-bottom: 0.2rem;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(255,255,255,0.08);
        }

        .hero {
            background: linear-gradient(135deg, #0B1F3A 0%, #243B73 100%);
            border-radius: 22px;
            padding: 2rem 2.2rem;
            color: white;
            margin-bottom: 1.4rem;
            box-shadow: 0 12px 35px rgba(11,31,58,.12);
        }

        .hero * {
            color: white !important;
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            margin-top: .4rem;
            opacity: .78;
            font-size: .98rem;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1.35rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 16px rgba(16,24,40,.045);
        }

        .card:hover {
            box-shadow: 0 8px 25px rgba(16,24,40,.075);
        }

        .section-title {
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 800;
            margin: .2rem 0 .25rem;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: .88rem;
            margin-bottom: 1rem;
        }

        .eyebrow {
            color: var(--muted);
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .11em;
            text-transform: uppercase;
        }

        .metric {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.15rem;
            min-height: 105px;
            box-shadow: 0 3px 14px rgba(16,24,40,.04);
        }

        .metric-icon {
            font-size: 1.2rem;
            margin-bottom: .35rem;
        }

        .metric-value {
            color: var(--navy);
            font-size: 1.7rem;
            font-weight: 850;
            line-height: 1;
        }

        .metric-label {
            color: var(--muted);
            font-size: .76rem;
            margin-top: .4rem;
        }

        .ats-box {
            text-align: center;
            padding: .3rem 0;
        }

        .ats-ring {
            --score: 0;
            --ring-color: #4F46E5;
            width: 142px;
            height: 142px;
            margin: 0 auto;
            border-radius: 50%;
            background:
                conic-gradient(
                    var(--ring-color) calc(var(--score) * 1%),
                    #E9ECF2 0
                );
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        .ats-ring::before {
            content: "";
            position: absolute;
            width: 112px;
            height: 112px;
            background: white;
            border-radius: 50%;
        }

        .ats-center {
            position: relative;
            z-index: 2;
            text-align: center;
        }

        .ats-number {
            color: var(--navy);
            font-size: 1.8rem;
            font-weight: 900;
            line-height: 1;
        }

        .ats-label {
            color: var(--muted);
            font-size: .63rem;
            font-weight: 800;
            letter-spacing: .08em;
            margin-top: .25rem;
        }

        .match-label {
            font-weight: 800;
            font-size: .82rem;
            margin-top: .55rem;
        }

        .job-rank {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 30px;
            height: 30px;
            border-radius: 9px;
            background: #EEF0FD;
            color: var(--blue);
            font-size: .75rem;
            font-weight: 850;
        }

        .job-title {
            color: var(--navy);
            font-size: 1.25rem;
            font-weight: 850;
            margin-top: .6rem;
        }

        .company {
            color: #475467;
            font-size: .9rem;
            font-weight: 650;
            margin-top: .25rem;
        }

        .job-meta {
            color: var(--muted);
            font-size: .8rem;
            margin-top: .3rem;
        }

        .pill {
            display: inline-block;
            padding: .27rem .62rem;
            border-radius: 999px;
            font-size: .72rem;
            font-weight: 700;
            margin: .18rem .18rem .18rem 0;
        }

        .pill-green { background: #EAF8EF; color: #138A3D; }
        .pill-red { background: #FDECEC; color: #C62828; }
        .pill-blue { background: #EEF0FD; color: #4338CA; }

        .reason {
            background: #F7F8FC;
            border: 1px solid #ECEEF4;
            border-radius: 12px;
            padding: .8rem;
            color: #475467;
            font-size: .82rem;
            line-height: 1.5;
            margin-top: .8rem;
        }

        .status {
            display: inline-block;
            padding: .3rem .65rem;
            border-radius: 999px;
            font-size: .7rem;
            font-weight: 800;
        }

        .status-pending { background:#FFF3DC; color:#A15C00; }
        .status-approved { background:#EEF0FD; color:#4338CA; }
        .status-applied { background:#F1EBFD; color:#6D28D9; }
        .status-interview { background:#E9F2FF; color:#1D4ED8; }
        .status-rejected { background:#FDECEC; color:#C62828; }
        .status-hired { background:#EAF8EF; color:#138A3D; }

        .timeline {
            border-left: 2px solid #E4E7EC;
            margin: .8rem 0 .4rem .45rem;
            padding-left: 1.2rem;
        }

        .timeline-item {
            position: relative;
            padding-bottom: 1rem;
        }

        .timeline-dot {
            position: absolute;
            left: -1.58rem;
            top: .15rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #D0D5DD;
            border: 3px solid white;
            box-shadow: 0 0 0 1px #D0D5DD;
        }

        .timeline-done .timeline-dot {
            background: #16A34A;
            box-shadow: 0 0 0 1px #16A34A;
        }

        .timeline-title {
            font-weight: 750;
            font-size: .84rem;
        }

        .timeline-date {
            color: var(--muted);
            font-size: .72rem;
            margin-top: .15rem;
        }

        .stButton > button,
        .stLinkButton > a {
            border-radius: 10px !important;
            font-weight: 750 !important;
            min-height: 40px;
        }

        .stButton > button[kind="primary"] {
            background: var(--navy) !important;
            border-color: var(--navy) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--blue) !important;
            border-color: var(--blue) !important;
        }

        @media (max-width: 900px) {
            .hero-title { font-size: 1.55rem; }
            .ats-ring { width: 125px; height: 125px; }
            .ats-ring::before { width: 98px; height: 98px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def load_applications():
    try:
        rows = get_applications() or []
        return [dict(zip(APP_FIELDS, row)) for row in rows]
    except Exception as exc:
        print(f"Database error: {exc}")
        return []


def score_value(value):
    try:
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def match_level(score):
    score = score_value(score)
    if score >= 90:
        return "Excellent Match", "#16A34A"
    if score >= 80:
        return "Strong Match", "#2563EB"
    if score >= 70:
        return "Good Match", "#4F46E5"
    if score >= 60:
        return "Moderate Match", "#D97706"
    return "Low Match", "#DC2626"


def status_class(status):
    return {
        "Pending Approval": "status-pending",
        "Approved": "status-approved",
        "Applied": "status-applied",
        "Interview": "status-interview",
        "Rejected": "status-rejected",
        "Hired": "status-hired",
    }.get(status, "status-pending")


def sync_job_statuses(jobs):
    """
    Read the current status from the database and merge it into
    the in-memory job result. This prevents the Find Jobs page
    from showing stale 'Pending Approval' after an action.
    """
    apps = load_applications()

    by_id = {}
    by_url = {}

    for app in apps:
        app_id = app.get("application_id")
        url = app.get("job_url")

        if app_id is not None:
            by_id[str(app_id)] = app

        if url:
            by_url[str(url)] = app

    for job in jobs:
        app_id = job.get("application_id")
        url = job.get("url")

        app = None

        if app_id is not None:
            app = by_id.get(str(app_id))

        if app is None and url:
            app = by_url.get(str(url))

        if app:
            job["application_status"] = app.get(
                "status",
                job.get("application_status", "Pending Approval"),
            )

            # Keep the DB score if the workflow result does not have one.
            if not job.get("ats_score"):
                job["ats_score"] = app.get("ats_score", 0)

    return jobs


def metric_card(label, value, icon):
    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ats_circle(score):
    score = score_value(score)
    label, color = match_level(score)

    st.markdown(
        f"""
        <div class="ats-box">
            <div class="ats-ring"
                 style="--score:{score};--ring-color:{color};">
                <div class="ats-center">
                    <div class="ats-number">{score:.0f}%</div>
                    <div class="ats-label">ATS MATCH</div>
                </div>
            </div>
            <div class="match-label" style="color:{color};">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def skill_pills(items, kind="green"):
    if isinstance(items, str):
        items = [x.strip() for x in items.split(",") if x.strip()]

    items = items or []

    if not items:
        st.caption("None detected.")
        return

    css = "pill-green" if kind == "green" else "pill-red"

    html = "".join(
        f'<span class="pill {css}">{str(item)}</span>'
        for item in items
    )

    st.markdown(html, unsafe_allow_html=True)


def status_badge(status):
    status = status or "Pending Approval"
    cls = status_class(status)

    st.markdown(
        f'<span class="status {cls}">{status}</span>',
        unsafe_allow_html=True,
    )


def empty_state(icon, title, subtitle):
    st.markdown(
        f"""
        <div class="card" style="text-align:center;padding:3rem;">
            <div style="font-size:2.4rem;">{icon}</div>
            <div style="font-size:1.1rem;font-weight:800;color:#172033;margin-top:.5rem;">
                {title}
            </div>
            <div style="color:#667085;margin-top:.35rem;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(label, value):
    value = score_value(value)
    _, color = match_level(value)

    st.markdown(
        f"""
        <div style="margin-bottom:.7rem;">
            <div style="display:flex;justify-content:space-between;
                        font-size:.78rem;font-weight:700;color:#344054;">
                <span>{label}</span>
                <span>{value:.0f}%</span>
            </div>
            <div style="height:7px;background:#EAECF0;border-radius:99px;margin-top:5px;">
                <div style="width:{value}%;height:7px;background:{color};
                            border-radius:99px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timeline(app):
    events = [
        ("Job Found", app.get("created_date")),
        ("Human Approved", app.get("approved_date")),
        ("Application Submitted", app.get("applied_date")),
        ("Interview", app.get("interview_date")),
    ]

    status = app.get("status", "")

    if status in ("Rejected", "Hired"):
        events.append((status, app.get("last_updated")))
    else:
        events.append(("Hired", None))

    st.markdown('<div class="timeline">', unsafe_allow_html=True)

    for title, date_value in events:
        done = bool(date_value)

        st.markdown(
            f"""
            <div class="timeline-item {'timeline-done' if done else ''}">
                <div class="timeline-dot"></div>
                <div class="timeline-title">{title}</div>
                <div class="timeline-date">
                    {date_value if date_value else "Waiting"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:.7rem 0 1.4rem;">
                <div style="font-size:1.35rem;font-weight:900;">
                    🎯 AI Job Hunter
                </div>
                <div style="font-size:.78rem;opacity:.7;margin-top:.3rem;">
                    Intelligent Career Automation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        icons = {
            "Dashboard": "⌂",
            "Find Jobs": "⌕",
            "Applications": "▣",
            "Resume Analysis": "▤",
        }

        labels = [f"{icons[p]}   {p}" for p in PAGES]

        if "page" not in st.session_state:
            st.session_state.page = "Dashboard"

        current_index = PAGES.index(st.session_state.page)

        selected = st.radio(
            "Navigation",
            labels,
            index=current_index,
            label_visibility="collapsed",
        )

        st.session_state.page = PAGES[labels.index(selected)]

        st.markdown("---")

        st.markdown(
            '<div style="font-size:.68rem;font-weight:800;letter-spacing:.1em;'
            'text-transform:uppercase;opacity:.6;margin-bottom:.7rem;">SYSTEM STATUS</div>',
            unsafe_allow_html=True,
        )

        for item in [
            "AI Agent Online",
            "Job Search Online",
            "Database Connected",
        ]:
            st.markdown(
                f'<div style="font-size:.78rem;margin:.45rem 0;">'
                f'<span style="color:#34D399;">●</span>&nbsp; {item}</div>',
                unsafe_allow_html=True,
            )

    return st.session_state.page


def dashboard():
    hour = datetime.now().hour
    greeting = (
        "Good morning" if hour < 12
        else "Good afternoon" if hour < 18
        else "Good evening"
    )

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">{greeting} 👋</div>
            <div class="hero-subtitle">
                Your AI-powered job search command center.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    apps = load_applications()

    counts = {x: 0 for x in STATUS_ORDER}

    for app in apps:
        if app.get("status") in counts:
            counts[app["status"]] += 1

    total_jobs = st.session_state.get("job_count", 0)

    cols = st.columns(6)

    values = [
        ("Jobs Found", total_jobs, "🔎"),
        ("Pending", counts["Pending Approval"], "⏳"),
        ("Approved", counts["Approved"], "✓"),
        ("Applied", counts["Applied"], "📨"),
        ("Interviews", counts["Interview"], "🎤"),
        ("Hired", counts["Hired"], "🏆"),
    ]

    for col, (label, value, icon) in zip(cols, values):
        with col:
            metric_card(label, value, icon)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown(
            """
            <div class="card">
                <div class="section-title">Your AI workflow</div>
                <div class="section-subtitle">
                    From resume to hiring — with human approval before applying.
                </div>

                <div style="display:flex;gap:10px;flex-wrap:wrap;">
                    <span class="pill pill-blue">01 Resume</span>
                    <span class="pill pill-blue">02 AI Analysis</span>
                    <span class="pill pill-blue">03 Job Search</span>
                    <span class="pill pill-blue">04 ATS Matching</span>
                    <span class="pill pill-blue">05 Human Approval</span>
                    <span class="pill pill-green">06 Apply & Track</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        pending = counts["Pending Approval"]

        st.markdown(
            f"""
            <div class="card">
                <div class="eyebrow">Attention Needed</div>
                <div style="font-size:1.65rem;font-weight:850;color:#0B1F3A;margin-top:.35rem;">
                    {pending}
                </div>
                <div style="color:#667085;font-size:.82rem;margin-top:.25rem;">
                    applications waiting for your approval
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def run_workflow(resume_file):
    with open("temp_resume.pdf", "wb") as f:
        f.write(resume_file.getbuffer())

    initial_state = {
        "resume_path": "temp_resume.pdf",
        "resume_text": "",
        "job_role": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "jobs": [],
        "eligible_jobs": [],
        "current_job": {},
        "job_description": "",
        "ats_score": 0.0,
        "ats_scores": [],
        "improvement": "",
        "approval_status": "",
        "application_status": "",
        "application_id": 0,
        "application_ids": [],
    }

    with st.status(
        "AI is analyzing your career profile...",
        expanded=True
    ) as box:

        st.write("Reading resume...")
        time.sleep(.15)

        st.write("Identifying skills and target roles...")
        time.sleep(.15)

        st.write("Searching jobs in India...")
        time.sleep(.15)

        st.write("Calculating ATS score for every job...")

        try:
            result = workflow.invoke(initial_state)
        except Exception as exc:
            print(f"Workflow error: {exc}")
            box.update(
                label="Analysis failed",
                state="error",
            )
            st.error(
                "The AI workflow could not complete. "
                "Check the terminal for the technical error."
            )
            return None

        box.update(
            label="Analysis completed",
            state="complete",
        )

    return result


def get_application_status(application_id):
    if not application_id:
        return None

    apps = load_applications()

    for app in apps:
        if str(app.get("application_id")) == str(application_id):
            return app.get("status")

    return None


def approve_job(application_id):
    if not application_id:
        st.warning("No database application ID is attached to this job.")
        return

    current_status = get_application_status(application_id)

    if current_status and current_status != "Pending Approval":
        st.info(f"This job is already {current_status}.")
        st.rerun()

    update_status(application_id, "Approved")
    st.success("Job approved. You can now apply.")
    st.rerun()


def apply_job(application_id):
    if not application_id:
        st.warning("No database application ID is attached to this job.")
        return

    current_status = get_application_status(application_id)

    if current_status != "Approved":
        st.warning(
            "This job must be approved before it can be marked as applied."
        )
        return

    # IMPORTANT:
    # This changes the tracker status to Applied.
    # It does not pretend to submit an application to a third-party
    # website. Actual external submission requires a supported
    # integration/browser automation flow.
    update_status(application_id, "Applied")
    st.success("Application marked as applied.")
    st.rerun()


def reject_job(application_id):
    if not application_id:
        st.warning("No database application ID is attached to this job.")
        return

    reject_application(
        application_id,
        "Rejected by user",
    )
    st.warning("Job rejected.")
    st.rerun()


def update_application_status(application_id, new_status):
    if not application_id:
        st.warning("No database application ID is attached to this job.")
        return

    update_status(application_id, new_status)
    st.rerun()


def render_job_card(job, rank):
    score = score_value(job.get("ats_score", 0))
    title = job.get("title", "Untitled Role")
    company = job.get("company", "Unknown Company")
    location = job.get("location", "India")
    employment = job.get("employment_type", "")
    url = job.get("url", "")
    matched = job.get("matched_skills", []) or []
    missing = job.get("missing_skills", []) or []
    app_id = job.get("application_id")
    eligibility = job.get("eligibility", "")
    reason = job.get("ats_reason", "")

    db_status = get_application_status(app_id)
    application_status = (
        db_status
        or job.get("application_status")
        or "Pending Approval"
    )

    job["application_status"] = application_status

    st.markdown('<div class="card">', unsafe_allow_html=True)

    left, middle, right = st.columns([4.2, 2.1, 3])

    with left:
        st.markdown(
            f'<span class="job-rank">#{rank}</span>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="job-title">{title}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="company">{company}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="job-meta">📍 {location}'
            f'{("  ·  " + employment) if employment else ""}</div>',
            unsafe_allow_html=True,
        )

        if eligibility:
            st.markdown(
                f"""
                <div style="margin-top:.8rem;">
                    <span class="pill pill-blue">{eligibility}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with middle:
        ats_circle(score)

    with right:
        if url:
            st.link_button(
                "View Job ↗",
                url,
                use_container_width=True,
            )

        if app_id:
            # ------------------------------------------------
            # PENDING APPROVAL
            # ------------------------------------------------
            if application_status == "Pending Approval":

                st.markdown(
                    '<div style="margin:.55rem 0 .4rem;">'
                    '<span class="status status-pending">'
                    'PENDING APPROVAL'
                    '</span></div>',
                    unsafe_allow_html=True,
                )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "✓ Approve",
                        key=f"approve_{app_id}_{rank}",
                        type="primary",
                        use_container_width=True,
                    ):
                        approve_job(app_id)

                with c2:
                    if st.button(
                        "✕ Reject",
                        key=f"reject_{app_id}_{rank}",
                        use_container_width=True,
                    ):
                        reject_job(app_id)

          
            elif application_status == "Approved":

                st.markdown(
                    '<div style="margin:.55rem 0 .4rem;">'
                    '<span class="status status-approved">'
                    '✓ APPROVED'
                    '</span></div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "🚀 Apply Now",
                    key=f"apply_{app_id}_{rank}",
                    type="primary",
                    use_container_width=True,
                ):
                    apply_job(app_id)

                if st.button(
                    "Undo Approval",
                    key=f"undo_{app_id}_{rank}",
                    use_container_width=True,
                ):
                    update_application_status(
                        app_id,
                        "Pending Approval",
                    )

            elif application_status == "Applied":

                st.markdown(
                    '<div style="margin:.55rem 0 .4rem;">'
                    '<span class="status status-applied">'
                    '✓ APPLICATION SUBMITTED'
                    '</span></div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "🎤 Mark Interview",
                    key=f"interview_{app_id}_{rank}",
                    use_container_width=True,
                ):
                    update_application_status(
                        app_id,
                        "Interview",
                    )

            elif application_status == "Interview":

                status_badge("Interview")

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        "🏆 Hired",
                        key=f"hired_{app_id}_{rank}",
                        type="primary",
                        use_container_width=True,
                    ):
                        update_application_status(
                            app_id,
                            "Hired",
                        )

                with c2:
                    if st.button(
                        "✕ Rejected",
                        key=f"int_reject_{app_id}_{rank}",
                        use_container_width=True,
                    ):
                        reject_job(app_id)

            elif application_status == "Hired":

                st.markdown(
                    '<div style="margin:.55rem 0 .4rem;">'
                    '<span class="status status-hired">'
                    '🏆 HIRED'
                    '</span></div>',
                    unsafe_allow_html=True,
                )

            elif application_status == "Rejected":

                st.markdown(
                    '<div style="margin:.55rem 0 .4rem;">'
                    '<span class="status status-rejected">'
                    '✕ REJECTED'
                    '</span></div>',
                    unsafe_allow_html=True,
                )

    st.markdown(
        "<hr style='border:0;border-top:1px solid #EAECF0;'>",
        unsafe_allow_html=True,
    )

    s1, s2 = st.columns(2)

    with s1:
        st.markdown(
            '<div class="eyebrow">MATCHED SKILLS</div>',
            unsafe_allow_html=True,
        )
        skill_pills(matched, "green")

    with s2:
        st.markdown(
            '<div class="eyebrow">MISSING SKILLS</div>',
            unsafe_allow_html=True,
        )
        skill_pills(missing, "red")

    if reason:
        st.markdown(
            f"""
            <div class="reason">
                <b>Why this matches:</b><br>
                {reason}
            </div>
            """,
            unsafe_allow_html=True,
        )

    breakdown = [
        ("Skills", job.get("skill_score", 0)),
        ("Keywords", job.get("keyword_score", 0)),
        ("Experience", job.get("experience_score", 0)),
        ("Role Match", job.get("role_score", 0)),
        ("Education", job.get("education_score", 0)),
        ("Projects", job.get("project_score", 0)),
    ]

    if any(score_value(x[1]) > 0 for x in breakdown):
        with st.expander("View ATS Breakdown"):
            for label, value in breakdown:
                progress_bar(label, value)

    if job.get("description"):
        with st.expander("View Job Description"):
            st.write(job["description"])

    st.markdown("</div>", unsafe_allow_html=True)


def render_job_results(result):
    jobs = result.get("jobs") or []

    st.markdown(
        """
        <div style="display:flex;align-items:end;justify-content:space-between;">
            <div>
                <div class="section-title">Recommended Jobs</div>
                <div class="section-subtitle">
                    Every job is independently evaluated against your resume.
                    You decide which jobs to approve and apply to.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not jobs:
        empty_state(
            "🔎",
            "No matching jobs found",
            "Try another resume or job profile.",
        )
        return

    jobs = sync_job_statuses(jobs)

    jobs = sorted(
        jobs,
        key=lambda j: score_value(j.get("ats_score", 0)),
        reverse=True,
    )

    strong_matches = [
        j for j in jobs
        if score_value(j.get("ats_score", 0)) >= 70
    ]

    pending = [
        j for j in jobs
        if (j.get("application_status") or "Pending Approval")
        == "Pending Approval"
    ]

    approved = [
        j for j in jobs
        if j.get("application_status") == "Approved"
    ]

    applied = [
        j for j in jobs
        if j.get("application_status") == "Applied"
    ]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Jobs Analyzed", len(jobs), "🔎")

    with c2:
        metric_card("Strong Matches", len(strong_matches), "✓")

    with c3:
        metric_card("Pending Approval", len(pending), "⏳")

    with c4:
        metric_card("Approved / Applied", len(approved) + len(applied), "🚀")

    st.markdown("<br>", unsafe_allow_html=True)

    for rank, job in enumerate(jobs, start=1):
        render_job_card(job, rank)


def find_jobs():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Find your next opportunity</div>
            <div class="hero-subtitle">
                Upload your resume. AI searches jobs in India and scores every job independently.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-title">Upload your resume</div>
        <div class="section-subtitle">
            PDF only · Your resume is analyzed before job matching.
        </div>
        """,
        unsafe_allow_html=True,
    )

    resume = st.file_uploader(
        "Resume PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if resume:
        st.success(f"✓ {resume.name} uploaded")

        if st.button(
            "Analyze Resume & Find Jobs",
            type="primary",
            use_container_width=True,
        ):
            result = run_workflow(resume)

            if result:
                st.session_state.job_result = result
                st.session_state.job_count = len(
                    result.get("jobs", []) or []
                )
                st.session_state.page = "Find Jobs"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("job_result"):
        render_job_results(
            st.session_state.job_result
        )


def resume_analysis():
    result = st.session_state.get("job_result")

    if not result:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-title">Resume Intelligence</div>
                <div class="hero-subtitle">
                    Understand how AI sees your profile.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        empty_state(
            "📄",
            "No resume analysis yet",
            "Go to Find Jobs and upload your PDF resume.",
        )
        return

    role = result.get("job_role", "Not detected")

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow" style="color:#B8C5E5;">TARGET ROLE</div>
            <div class="hero-title">{role}</div>
            <div class="hero-subtitle">
                AI-generated profile analysis and job compatibility.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    jobs = result.get("jobs") or []

    if jobs:
        best = max(
            jobs,
            key=lambda j: score_value(j.get("ats_score", 0))
        )

        c1, c2, c3 = st.columns([1, 2.2, 1])

        with c1:
            ats_circle(best.get("ats_score", 0))

        with c2:
            st.markdown(
                f"""
                <div class="card" style="height:100%;">
                    <div class="eyebrow">BEST MATCHING ROLE</div>
                    <div style="font-size:1.35rem;font-weight:850;color:#0B1F3A;margin-top:.4rem;">
                        {best.get("title", "—")}
                    </div>
                    <div style="font-weight:650;color:#475467;margin-top:.25rem;">
                        {best.get("company", "—")}
                    </div>
                    <div style="color:#667085;font-size:.8rem;margin-top:.25rem;">
                        {best.get("location", "—")}
                    </div>
                    <div class="reason">
                        This is your highest ATS match among
                        {len(jobs)} jobs analyzed.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:
            metric_card("Jobs Analyzed", len(jobs), "🔎")
            metric_card(
                "Strong Matches",
                len([
                    j for j in jobs
                    if score_value(j.get("ats_score", 0)) >= 70
                ]),
                "✓",
            )

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="card"><div class="section-title">Technical Skills</div>',
            unsafe_allow_html=True,
        )
        skill_pills(result.get("skills", ""), "green")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="card">
                <div class="section-title">Experience</div>
                <div style="color:#475467;line-height:1.6;margin-top:.6rem;">
                    {result.get("experience", "Not detected")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="card">
                <div class="section-title">Education</div>
                <div style="color:#475467;line-height:1.6;margin-top:.6rem;">
                    {result.get("education", "Not detected")}
                </div>
            </div>

            <div class="card">
                <div class="section-title">Projects</div>
                <div style="color:#475467;line-height:1.6;margin-top:.6rem;">
                    {result.get("projects", "Not detected")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result.get("improvement"):
        with st.expander("AI Resume Improvement Suggestions"):
            st.write(result["improvement"])

    st.markdown("<br>", unsafe_allow_html=True)
    render_job_results(result)

def application_card(app):
    app_id = app["application_id"]
    score = score_value(app.get("ats_score", 0))
    status = app.get("status", "Pending Approval")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    left, middle, right = st.columns([4, 1.5, 2.5])

    with left:
        st.markdown(
            f"""
            <div style="font-size:1.05rem;font-weight:850;color:#0B1F3A;">
                {app["job_title"]}
            </div>
            <div style="color:#475467;font-weight:650;margin-top:.2rem;">
                {app["company"]}
            </div>
            <div style="color:#667085;font-size:.78rem;margin-top:.2rem;">
                📍 {app["location"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with middle:
        ats_circle(score)

    with right:
        status_badge(status)

        st.markdown("<br>", unsafe_allow_html=True)

        if app.get("job_url"):
            st.link_button(
                "View Job ↗",
                app["job_url"],
                use_container_width=True,
            )

        if status == "Pending Approval":

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "✓ Approve",
                    key=f"app_approve_{app_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    approve_job(app_id)

            with c2:
                if st.button(
                    "✕ Reject",
                    key=f"app_reject_{app_id}",
                    use_container_width=True,
                ):
                    reject_job(app_id)

        elif status == "Approved":

            if st.button(
                "🚀 Apply Now",
                key=f"app_apply_{app_id}",
                type="primary",
                use_container_width=True,
            ):
                apply_job(app_id)

        elif status == "Applied":

            if st.button(
                "🎤 Mark Interview",
                key=f"app_interview_{app_id}",
                use_container_width=True,
            ):
                update_status(app_id, "Interview")
                st.rerun()

        elif status == "Interview":

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "🏆 Hired",
                    key=f"app_hired_{app_id}",
                    type="primary",
                    use_container_width=True,
                ):
                    update_status(app_id, "Hired")
                    st.rerun()

            with c2:
                if st.button(
                    "✕ Rejected",
                    key=f"app_int_reject_{app_id}",
                    use_container_width=True,
                ):
                    reject_job(app_id)

        elif status == "Rejected":
            st.caption("This application was rejected.")

        elif status == "Hired":
            st.caption("🎉 Candidate marked as hired.")

    with st.expander("Application Timeline"):
        render_timeline(app)

    st.markdown("</div>", unsafe_allow_html=True)


def applications():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Application Tracker</div>
            <div class="hero-subtitle">
                Track every opportunity from approval to interview and hiring.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    apps = load_applications()

    counts = {x: 0 for x in STATUS_ORDER}

    for app in apps:
        if app.get("status") in counts:
            counts[app["status"]] += 1

    cols = st.columns(6)

    for col, status in zip(cols, STATUS_ORDER):
        with col:
            metric_card(
                status,
                counts[status],
                {
                    "Pending Approval": "⏳",
                    "Approved": "✓",
                    "Applied": "📨",
                    "Interview": "🎤",
                    "Rejected": "↘",
                    "Hired": "🏆",
                }[status],
            )

    st.markdown("<br>", unsafe_allow_html=True)

    if not apps:
        empty_state(
            "📋",
            "No applications yet",
            "Approve a recommended job to start tracking it.",
        )
        return

    selected_status = st.selectbox(
        "Filter applications",
        ["All"] + STATUS_ORDER,
    )

    filtered = (
        apps
        if selected_status == "All"
        else [
            x for x in apps
            if x["status"] == selected_status
        ]
    )

    if not filtered:
        empty_state(
            "📭",
            f"No {selected_status} applications",
            "Try another status filter.",
        )
        return

    for app in filtered:
        application_card(app)


def main():
    inject_css()
    page = sidebar()

    if page == "Dashboard":
        dashboard()

    elif page == "Find Jobs":
        find_jobs()

    elif page == "Applications":
        applications()

    elif page == "Resume Analysis":
        resume_analysis()


if __name__ == "__main__":
    main()
