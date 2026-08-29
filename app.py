import os
import base64
import streamlit as st
from dotenv import load_dotenv
from agents import workflow
import database as db

# Load environment variables
load_dotenv()

# Initialize Database
db.create_table()

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AI Job Hunter | Executive Resume Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to convert local image to base64
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

LOGO_PATH = r"C:\Users\Utkar\.gemini\antigravity-ide\brain\707f8347-e1fe-42d5-b0ab-17d8789a8012\ai_job_hunter_logo_1788025423140.png"
logo_b64 = get_image_base64(LOGO_PATH)

# =========================================================
# VIOLET DESIGN SYSTEM (PRODUCTION CLEAN CSS)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Typography & Canvas */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background-color: #FAFAFD !important;
    color: #0F172A !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #F8F7FF !important;
    border-right: 1px solid #E0D9FA !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] h5,
[data-testid="stSidebar"] h6 {
    color: #1E1B4B !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label {
    color: #334155 !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #64748B !important;
}

/* Header Banner Card */
.hero-banner {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 50%, #7C3AED 100%);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    color: #FFFFFF;
    margin-bottom: 1.8rem;
    box-shadow: 0 12px 30px -5px rgba(79, 70, 229, 0.3);
}

.hero-banner h1 {
    color: #FFFFFF !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.4rem !important;
    letter-spacing: -0.02em;
}

.hero-banner p {
    color: #E0E7FF !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    margin-bottom: 0 !important;
}

/* Cards & Containers */
.v-card {
    background: #FFFFFF;
    border: 1px solid #EDE9FE;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 15px -2px rgba(99, 102, 241, 0.05);
}

/* Skill Badges */
.skill-badge {
    display: inline-block;
    background: #F5F3FF;
    border: 1px solid #DDD6FE;
    color: #4F46E5;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    margin-right: 0.4rem;
    margin-bottom: 0.5rem;
}

/* Job Pill */
.job-meta-tag {
    display: inline-block;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    color: #334155;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    margin-right: 0.5rem;
}

/* ATS Score Badges */
.ats-badge-high {
    background: #ECFDF5;
    border: 3px solid #10B981;
    color: #047857;
    font-size: 2.2rem;
    font-weight: 800;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ats-badge-mid {
    background: #FFFBEB;
    border: 3px solid #F59E0B;
    color: #B45309;
    font-size: 2.2rem;
    font-weight: 800;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ats-badge-low {
    background: #FEF2F2;
    border: 3px solid #EF4444;
    color: #B91C1C;
    font-size: 2.2rem;
    font-weight: 800;
    width: 90px;
    height: 90px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    border-bottom: 2px solid #EDE9FE;
    padding-bottom: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: #64748B !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 10px !important;
}

.stTabs [aria-selected="true"] {
    color: #4F46E5 !important;
    background: #EEF2FF !important;
    border: 1px solid #C7D2FE !important;
}

/* File Uploader */
div[data-testid="stFileUploader"] {
    border: 2px dashed #C7D2FE !important;
    border-radius: 16px !important;
    background: #FFFFFF !important;
    padding: 1rem !important;
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# TOP LOGO BRANDING BAR
# =========================================================
if logo_b64:
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF; border:1px solid #EDE9FE; border-radius:18px; padding:0.9rem 2rem; margin-bottom:1.5rem; box-shadow:0 6px 20px -4px rgba(99, 102, 241, 0.06);">
        <div style="display:flex; align-items:center; gap:1.2rem;">
            <img src="data:image/png;base64,{logo_b64}" style="width:52px; height:52px; border-radius:14px; object-fit:cover; box-shadow:0 4px 14px rgba(79,70,229,0.3);" alt="AI Job Hunter Logo">
            <div>
                <div style="font-size:1.5rem; font-weight:800; color:#0F172A; letter-spacing:-0.025em; line-height:1.2;">AI Job Hunter</div>
                <div style="font-size:0.85rem; font-weight:600; color:#6366F1;">Executive Resume Intelligence & Job Matching Engine</div>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="background:#EEF2FF; border:1px solid #C7D2FE; color:#4F46E5; font-size:0.8rem; font-weight:700; padding:0.4rem 0.95rem; border-radius:9999px;">⚡ Gemini 2.5 Active</span>
            <span style="background:#ECFDF5; border:1px solid #A7F3D0; color:#047857; font-size:0.8rem; font-weight:700; padding:0.4rem 0.95rem; border-radius:9999px;">🟢 System Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SIDEBAR SYSTEM DIAGNOSTICS & LOGO
# =========================================================
with st.sidebar:
    if logo_b64:
        st.markdown(f'''
        <div style="text-align:center; padding-top:0.5rem; margin-bottom:0.8rem;">
            <img src="data:image/png;base64,{logo_b64}" style="width:76px; height:76px; border-radius:20px; box-shadow:0 8px 24px rgba(79,70,229,0.25);" alt="AI Job Hunter Logo">
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center; margin-bottom:0.2rem;'>⚡ AI Job Hunter</h2>", unsafe_allow_html=True)
    st.caption("Executive Resume Intelligence & Job Matching")
    st.divider()


    st.markdown("""
    • **PDF Resume Parser**: LangGraph agent text extraction
    • **Role & Skill Profiler**: Gemini AI entity recognition
    • **ATS Evaluator**: 0-100% keyword & experience benchmark
    • **Live Job Matcher**: Real-time market opportunities
    • **Application Tracker**: SQLite application database
    • **AI Career Tools**: Cover Letter & Interview Prep
    """)


# =========================================================
# MAIN HERO BANNER
# =========================================================
st.markdown("""
<div class="hero-banner">
    <h1>⚡ AI Job Hunter</h1>
    <p>Enterprise Resume Profiling, ATS Scoring, Live Job Matching & Application Tracking</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# APPLICATION TABS
# =========================================================
tab_matcher, tab_tracker, tab_ai_tools, tab_settings = st.tabs([
    "🚀 Resume & Job Matcher",
    "📋 Application Tracker",
    "🤖 AI Career Tools",
    "⚙️ System Status"
])

# =========================================================
# TAB 1: RESUME & JOB MATCHER
# =========================================================
with tab_matcher:
    col_up, col_info = st.columns([1.1, 1], gap="large")

    with col_up:
        st.markdown("### 📄 Upload Candidate Resume")
        
        resume = st.file_uploader(
            "Select your PDF Resume",
            type=["pdf"],
            help="Upload your PDF resume to begin automated parsing, ATS scoring, and live job matching."
        )

        if resume is not None:
            st.success(f"✅ Loaded: `{resume.name}` ({round(len(resume.getbuffer())/1024, 1)} KB)")

            if st.button("🚀 Analyze Resume & Match Jobs", type="primary", use_container_width=True):
                # Write resume buffer to temp file
                with open("temp_resume.pdf", "wb") as f:
                    f.write(resume.getbuffer())

                initial_state = {
                    "resume_path": "temp_resume.pdf",
                    "resume_text": "",
                    "job_role": "",
                    "skills": "",
                    "experience": "",
                    "education": "",
                    "projects": "",
                    "jobs": [],
                    "job_description": "",
                    "ats_score": 0.0,
                    "improvement": ""
                }

                with st.spinner("🤖 Running Multi-Agent AI Workflow (Parsing -> Profiling -> ATS Scoring -> Job Search)..."):
                    try:
                        result = workflow.invoke(initial_state)
                        st.session_state["analysis_result"] = result
                        st.toast("Resume analysis & job matching completed!", icon="🎉")
                    except Exception as e:
                        st.error(f"❌ Error during workflow execution: {e}")
                        st.info("Ensure GOOGLE_API_KEY is configured in your `.env` or System Status tab.")

    with col_info:
        st.markdown("""
        <div class="v-card">
            <h4 style="margin-top:0; color:#4F46E5;">💡 Core System Architecture</h4>
            <ul style="color:#475569; padding-left:1.2rem; line-height:1.8;">
                <li><b>Multi-Agent Parser</b>: LangGraph state graph extracts raw text from PDF documents.</li>
                <li><b>Gemini Profiler</b>: Identifies target candidate role and technical skill matrix.</li>
                <li><b>ATS Evaluator</b>: Computes benchmark match score against real job descriptions.</li>
                <li><b>RapidAPI Job Search</b>: Fetches real-time market opportunities tailored to candidate profile.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


    # Display Results if available in session state
    if "analysis_result" in st.session_state:
        res = st.session_state["analysis_result"]
        st.divider()

        # Section 1: Candidate Profile & ATS Score
        st.markdown("## 📊 Candidate Executive Profile")
        
        c1, c2 = st.columns([1.2, 1], gap="large")

        with c1:
            st.markdown("#### 🎯 Target Candidate Role")
            st.markdown(f"<h3 style='color:#4F46E5; margin-top:0;'>{res.get('job_role', 'Not Specified')}</h3>", unsafe_allow_html=True)
            
            st.markdown("#### 🛠️ Technical Skill Matrix")
            skills_list = [s.strip() for s in res.get('skills', '').split(',') if s.strip()]
            if skills_list:
                skills_html = "".join([f'<span class="skill-badge">{s}</span>' for s in skills_list])
                st.markdown(skills_html, unsafe_allow_html=True)
            else:
                st.caption("No skills extracted")

        with c2:
            ats_score = res.get("ats_score", 0.0)
            badge_class = "ats-badge-high" if ats_score >= 80 else ("ats-badge-mid" if ats_score >= 60 else "ats-badge-low")
            status_text = "Excellent ATS Match" if ats_score >= 80 else ("Good Fit" if ats_score >= 60 else "Action Recommended")

            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:1.5rem; background:#FFFFFF; border:1px solid #EDE9FE; border-radius:16px; padding:1.5rem;">
                <div class="{badge_class}">{int(ats_score)}%</div>
                <div>
                    <div style="font-size:0.82rem; color:#64748B; font-weight:700; text-transform:uppercase;">ATS Benchmark Score</div>
                    <div style="font-size:1.3rem; font-weight:800; color:#0F172A;">{status_text}</div>
                    <div style="font-size:0.82rem; color:#64748B; margin-top:0.2rem;">Evaluated against top target market description</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if res.get("improvement"):
                with st.expander("🛠️ Actionable ATS Resume Improvements", expanded=False):
                    st.markdown(res["improvement"])

        # Detailed Breakdown Expander
        with st.expander("🔍 View Complete Parsed Candidate Details", expanded=False):
            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("**💼 Experience**")
                st.write(res.get("experience", "N/A"))
            with d2:
                st.markdown("**🎓 Education**")
                st.write(res.get("education", "N/A"))
            with d3:
                st.markdown("**🚀 Projects**")
                st.write(res.get("projects", "N/A"))

        st.divider()

        # Section 2: Live Job Matches
        st.markdown("## 🔎 Matched Live Opportunities")
        jobs = res.get("jobs", [])

        if not jobs:
            st.info("💡 No live jobs returned for this specific role query. Try refining your resume or checking your RapidAPI key.")
        else:
            st.success(f"🎯 Found **{len(jobs)}** job opportunities matching candidate profile `{res.get('job_role')}`.")
            
            for idx, job in enumerate(jobs, start=1):
                col_card, col_action = st.columns([3.5, 1], gap="medium")
                
                with col_card:
                    st.markdown(f"""
                    <div class="v-card">
                        <div style="font-size:1.25rem; font-weight:800; color:#0F172A;">{idx}. {job.get('title', 'Position Unspecified')}</div>
                        <div style="font-size:1rem; font-weight:700; color:#4F46E5; margin-bottom:0.6rem;">🏢 {job.get('company', 'Company Confidential')}</div>
                        <div>
                            <span class="job-meta-tag">📍 {job.get('location', 'Remote / Unspecified')}</span>
                            <span class="job-meta-tag">💼 {job.get('employment_type', 'Full-time')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander("📄 View Full Job Description"):
                        st.write(job.get("description", "No detailed description provided."))

                with col_action:
                    st.write("")
                    if job.get("url"):
                        st.link_button("🔗 View & Apply", job["url"], use_container_width=True)
                    
                    # Save Application Button
                    save_key = f"save_{idx}_{job.get('title')}"
                    if st.button("⭐ Save to Tracker", key=save_key, use_container_width=True):
                        db.save_application(
                            company=job.get("company", "Unknown"),
                            job_title=job.get("title", "Position"),
                            location=job.get("location", "Remote"),
                            job_url=job.get("url", ""),
                            ats_score=ats_score
                        )
                        st.toast(f"Saved '{job.get('title')}' to Application Tracker!", icon="✅")


# =========================================================
# TAB 2: APPLICATION TRACKER
# =========================================================
with tab_tracker:
    st.markdown("## 📋 Application Tracker Dashboard")
    st.markdown("Track and manage saved job applications stored in your SQLite database (`applications.db`).")

    applications = db.get_applications()

    if not applications:
        st.info("ℹ️ No applications saved yet. Click **⭐ Save to Tracker** on any job card in the Resume Matcher tab to add items here.")
    else:
        # Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        total_apps = len(applications)
        applied_cnt = sum(1 for a in applications if a[6] == "Applied")
        interview_cnt = sum(1 for a in applications if a[6] == "Interviewing")
        offer_cnt = sum(1 for a in applications if a[6] == "Offered")

        with m1:
            st.metric("Total Saved", total_apps)
        with m2:
            st.metric("Applied", applied_cnt)
        with m3:
            st.metric("Interviewing", interview_cnt)
        with m4:
            st.metric("Offered", offer_cnt)

        st.divider()

        # Display Saved Applications
        for app in applications:
            app_id, company, job_title, location, job_url, score, status, applied_date = app
            
            with st.container():
                c_info, c_status, c_link = st.columns([3, 1.5, 1], gap="medium")
                
                with c_info:
                    st.markdown(f"### **{job_title}**")
                    st.markdown(f"🏢 **{company}** &nbsp;•&nbsp; 📍 {location} &nbsp;•&nbsp; 🎯 Match Score: `{int(score if score else 0)}%` &nbsp;•&nbsp; 📅 Saved: {applied_date}")

                with c_status:
                    status_options = ["Applied", "Interviewing", "Offered", "Rejected"]
                    current_idx = status_options.index(status) if status in status_options else 0
                    
                    new_status = st.selectbox(
                        "Status",
                        options=status_options,
                        index=current_idx,
                        key=f"status_select_{app_id}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != status:
                        db.update_status(app_id, new_status)
                        st.toast(f"Updated status for '{job_title}' to {new_status}!", icon="🔄")
                        st.rerun()

                with c_link:
                    if job_url:
                        st.link_button("🔗 Apply Link", job_url, use_container_width=True)

                st.divider()


# =========================================================
# TAB 3: AI CAREER TOOLS
# =========================================================
with tab_ai_tools:
    st.markdown("## 🤖 AI Career Tools & Interview Prep")
    st.markdown("Leverage Gemini LLM to generate tailored cover letters and practice targeted interview questions.")

    tool_col1, tool_col2 = st.columns(2, gap="large")

    with tool_col1:
        st.markdown("### ✉️ AI Cover Letter Generator")
        st.caption("Generate a personalized, high-converting cover letter based on target role & company.")

        target_company = st.text_input("Target Company Name", placeholder="e.g. Google, Microsoft, Tech Corp")
        target_role_input = st.text_input("Target Job Title", placeholder="e.g. Senior Software Engineer")

        if st.button("✨ Generate Cover Letter", type="primary"):
            if target_company and target_role_input:
                with st.spinner("Writing personalized cover letter with Gemini AI..."):
                    from agents import get_llm, get_response_text
                    prompt = f"""Write a professional cover letter for the role of '{target_role_input}' at '{target_company}'.
Highlight technical expertise, problem-solving skills, and enthusiasm for the company."""
                    model = get_llm()
                    resp = model.invoke(prompt)
                    letter_text = get_response_text(resp)
                    st.success("Cover Letter Generated!")
                    st.text_area("Generated Cover Letter", value=letter_text, height=280)
            else:
                st.warning("Please provide both Company Name and Target Job Title.")

    with tool_col2:
        st.markdown("### 🎯 Interview Question Generator")
        st.caption("Get tailored technical & behavioral interview questions with answer guidelines.")

        prep_role = st.text_input("Role for Interview Prep", placeholder="e.g. Data Scientist / Frontend Lead")
        
        if st.button("🧠 Generate Q&A Prep", type="primary"):
            if prep_role:
                with st.spinner("Generating interview prep questions with Gemini AI..."):
                    from agents import get_llm, get_response_text
                    prompt = f"""Provide 3 technical and 2 behavioral interview questions for a candidate applying for '{prep_role}'.
For each question, provide a concise bulleted tip on how to structure the best response."""
                    model = get_llm()
                    resp = model.invoke(prompt)
                    prep_text = get_response_text(resp)
                    st.success("Interview Questions Ready!")
                    st.markdown(prep_text)
            else:
                st.warning("Please enter a role for interview preparation.")


# =========================================================
# TAB 4: SYSTEM STATUS & SETTINGS
# =========================================================
with tab_settings:
    st.markdown("## ⚙️ System Diagnostics & API Credentials")
    st.markdown("Manage environment keys and API connections for AI Job Hunter.")

    s1, s2 = st.columns(2, gap="large")

    with s1:
        st.markdown("#### 🔑 Google Gemini API Key")
        st.caption("Required for LangGraph agents, resume profiling, and ATS evaluation.")
        g_key_env = os.getenv("GOOGLE_API_KEY", "")
        new_g_key = st.text_input("GOOGLE_API_KEY", value=g_key_env, type="password")

    with s2:
        st.markdown("#### 🌐 RapidAPI JSearch Key")
        st.caption("Required to fetch real-time live job postings.")
        r_key_env = os.getenv("RAPIDAPI_KEY", "")
        new_r_key = st.text_input("RAPIDAPI_KEY", value=r_key_env, type="password")

    if st.button("💾 Save Credentials to `.env` File", type="primary"):
        env_content = f"""GOOGLE_API_KEY={new_g_key}
RAPIDAPI_KEY={new_r_key}
GEMINI_MODEL=gemini-2.5-flash
"""
        with open(".env", "w") as f:
            f.write(env_content)
        st.success("Credentials saved to `.env`! Restart server or rerun analysis to apply.")
