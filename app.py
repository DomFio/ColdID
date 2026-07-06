# app.py
# Streamlit UI for ColdIQ
# Run with: streamlit run app.py

import streamlit as st
from main import build_graph, extract_skills

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="ColdIQ",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0F1117;
        color: #FFFFFF;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1C1F2E;
        border-right: 1px solid #2E3250;
    }

    /* Score display */
    .score-container {
        text-align: center;
        padding: 20px;
        background: #1C1F2E;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    .score-number {
        font-size: 72px;
        font-weight: 700;
        font-family: monospace;
        line-height: 1;
    }

    .score-label {
        font-size: 14px;
        color: #8B8FA8;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Email display */
    .email-container {
        background: #1C1F2E;
        border: 1px solid #2E3250;
        border-radius: 12px;
        padding: 24px;
        font-family: sans-serif;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* Info cards */
    .info-card {
        background: #1C1F2E;
        border: 1px solid #2E3250;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Section headers */
    .section-header {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #8B8FA8;
        margin-bottom: 12px;
    }

    /* Approve button */
    .stButton > button {
        background-color: #4F8EF7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #3A7AE4;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---- SIDEBAR — JOB INPUT ----
with st.sidebar:
    st.markdown("# 🎯 ColdIQ")
    st.markdown("*AI-Powered Job Application Pipeline*")
    st.markdown("---")

    # Resume upload
    st.markdown("### Your Resume")
    resume_source = st.radio("Resume source", ["Upload PDF", "Upload TXT", "Paste text"])

    resume_text = ""
    if resume_source == "Upload PDF":
        resume_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
        if resume_file:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(resume_file.read())) as pdf:
                resume_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            st.success("✓ Resume loaded")
    elif resume_source == "Upload TXT":
        resume_file = st.file_uploader("Upload your resume (TXT)", type="txt")
        if resume_file:
            resume_text = resume_file.read().decode("utf-8")
            st.success("✓ Resume loaded")
    else:
        resume_text = st.text_area("Paste your resume", height=150, placeholder="Paste your resume text here...")

    st.markdown("---")

    st.markdown("### Job Details")

    # URL fetch option
    job_url = st.text_input("Job Posting URL (optional)", placeholder="Paste LinkedIn or Indeed URL...")
    fetch_button = st.button("🔍 Fetch Job Details", use_container_width=True)

    # Session state to hold fetched values
    if "fetched_title" not in st.session_state:
        st.session_state.fetched_title = ""
    if "fetched_company" not in st.session_state:
        st.session_state.fetched_company = ""
    if "fetched_description" not in st.session_state:
        st.session_state.fetched_description = ""

    if fetch_button and job_url:
        with st.spinner("Fetching job details from URL..."):
            from job_fetcher import fetch_job_from_url
            fetched = fetch_job_from_url(job_url)
            if "error" in fetched:
                st.error(fetched["error"])
            else:
                st.session_state.fetched_title = fetched.get("job_title", "")
                st.session_state.fetched_company = fetched.get("company_name", "")
                st.session_state.fetched_description = fetched.get("job_description", "")
                st.success("✓ Job details fetched successfully")

    job_title = st.text_input("Job Title", value=st.session_state.fetched_title, placeholder="e.g. ML Engineer")
    company_name = st.text_input("Company Name", value=st.session_state.fetched_company, placeholder="e.g. Acme Corp")

    st.markdown("### Job Description")
    jd_source = st.radio("Source", ["Paste text", "Upload job.txt"], horizontal=True)

    job_description = ""
    if jd_source == "Paste text":
        job_description = st.text_area("Job Description", value=st.session_state.fetched_description, height=200, placeholder="Paste the full job description here...")
    else:
        uploaded = st.file_uploader("Upload job.txt", type="txt")
        if uploaded:
            job_description = uploaded.read().decode("utf-8")
            st.success("✓ Job description loaded")

    st.markdown("### Hiring Manager (optional)")
    knows_hm = st.checkbox("I know the hiring manager")
    hiring_manager_name = ""
    hiring_manager_title = ""
    hiring_manager_linkedin = ""

    if knows_hm:
        hiring_manager_name = st.text_input("Name")
        hiring_manager_title = st.text_input("Title")
        hiring_manager_linkedin = st.text_input("LinkedIn URL")

    st.markdown("---")
    run_button = st.button("🚀 Run ColdIQ", use_container_width=True)

# ---- MAIN AREA ----
if not run_button:
    st.markdown("## Welcome to ColdIQ")
    st.markdown("Fill in the job details in the sidebar and click **Run ColdIQ** to start the pipeline.")
    st.markdown("""
    **What ColdIQ does:**
    1. 🎯 **Qualifies** how well you match the role
    2. 🔍 **Finds** the hiring manager automatically
    3. ✍️ **Drafts** a personalized cold email grounded in your real experience
    4. ✅ **Reviews** and refines the email before sending
    """)

else:
    if not job_title or not company_name or not job_description:
        st.error("Please fill in Job Title, Company Name, and Job Description before running.")
    else:
        # Build RAG from uploaded resume
        if resume_text:
            with st.spinner("Building knowledge base from your resume..."):
                from rag import build_vector_store_from_text, set_vector_store
                vector_store = build_vector_store_from_text(resume_text)
                set_vector_store(vector_store)
        else:
            st.warning("No resume provided — using default knowledge base from data/resume.txt")

        # Extract skills
        with st.spinner("Extracting required skills..."):
            required_skills = extract_skills(job_description)

        st.success(f"✓ Skills identified: {', '.join(required_skills)}")

        # Build pipeline input
        pipeline_input = {
            "job_title": job_title,
            "company_name": company_name,
            "job_description": job_description,
            "required_skills": required_skills,
            "qualifier_score": 0,
            "qualifier_reasoning": "",
            "hiring_manager_name": hiring_manager_name,
            "hiring_manager_title": hiring_manager_title,
            "hiring_manager_linkedin": hiring_manager_linkedin,
            "hiring_manager_email": "",
            "draft_email": "",
            "review_feedback": "",
            "approved": False,
            "review_loops": 0,
            "date_applied": "",
            "outcome": ""
        }

        # Run the pipeline
        with st.spinner("Running ColdIQ pipeline..."):
            app = build_graph()
            result = app.invoke(pipeline_input)

        # ---- RESULTS ----
        st.markdown("---")

        # Two column layout
        col1, col2 = st.columns([1, 2])

        with col1:
            # Qualifier score
            score = result['qualifier_score']
            score_color = "#4CAF50" if score >= 80 else "#FFC107" if score >= 60 else "#F44336"

            st.markdown(f"""
            <div class="score-container">
                <div class="score-number" style="color: {score_color}">{score}</div>
                <div class="score-label">Qualifier Score / 100</div>
            </div>
            """, unsafe_allow_html=True)

            # Qualifier reasoning
            st.markdown('<div class="section-header">Qualifier Reasoning</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card">{result["qualifier_reasoning"]}</div>', unsafe_allow_html=True)

            # Hiring manager
            st.markdown('<div class="section-header">Hiring Manager</div>', unsafe_allow_html=True)
            hm_name = result['hiring_manager_name'] or "Not found"
            hm_title = result['hiring_manager_title'] or ""
            hm_linkedin = result['hiring_manager_linkedin'] or ""
            st.markdown(f"""
            <div class="info-card">
                <strong>{hm_name}</strong><br>
                <span style="color: #8B8FA8">{hm_title}</span><br>
                {'<a href="' + hm_linkedin + '" style="color: #4F8EF7">LinkedIn Profile</a>' if hm_linkedin and hm_linkedin != "not found" else ""}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Draft email
            st.markdown('<div class="section-header">Draft Email</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="email-container">{result["draft_email"]}</div>', unsafe_allow_html=True)

            # Approve / reject buttons
            st.markdown("---")
            st.markdown('<div class="section-header">Human Approval</div>', unsafe_allow_html=True)

            approve_col, reject_col = st.columns(2)
            with approve_col:
                if st.button("✅ Approve & Send", use_container_width=True):
                    st.success("Email approved! (Sending functionality coming soon)")
            with reject_col:
                if st.button("❌ Reject & Rerun", use_container_width=True):
                    st.warning("Rerunning pipeline with feedback...")