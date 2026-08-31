import json
import re
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from pypdf import PdfReader
from job_search import search_jobs
from database import create_table, save_application


load_dotenv()

create_table()

ATS_THRESHOLD = 70.0

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
)


class JobAgentState(TypedDict, total=False):

    resume_path: str
    resume_text: str
    job_role: str
    skills: str
    experience: str
    education: str
    projects: str
    jobs: list
    eligible_jobs: list
    current_job: dict
    job_description: str
    ats_score: float
    ats_scores: list
    improvement: str
    approval_status: str
    application_status: str
    application_id: int
    application_ids: list


def get_response_text(response):
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text = ""

        for item in content:
            if isinstance(item, str):
                text += item

            elif isinstance(item, dict) and "text" in item:
                text += str(item["text"])

        return text

    return str(content)


def parse_json_response(result):
    if not result:
        return {}

    result = str(result).strip()

    result = re.sub(
        r"```json",
        "",
        result,
        flags=re.IGNORECASE,
    )

    result = re.sub(
        r"```",
        "",
        result,
    ).strip()

    try:
        data = json.loads(result)

        return data if isinstance(data, dict) else {}

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        result,
        re.DOTALL,
    )

    if match:
        try:
            data = json.loads(match.group())
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    return {}


def safe_score(value, default=0.0):
    try:
        score = float(value)
    except (ValueError, TypeError):
        score = default

    return round(
        max(0.0, min(score, 100.0)),
        2,
    )


def clean_list(value):
    if value is None:
        return []

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    if isinstance(value, list):
        result = []

        for item in value:
            item = str(item).strip()

            if item:
                result.append(item)

        return list(dict.fromkeys(result))

    return []


def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()

    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace("&", " and ")

    text = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def term_exists(term, text):
    if not term or not text:
        return False

    term = normalize_text(term)
    text = normalize_text(text)

    if not term:
        return False

    if term in text:
        return True

    if len(term.split()) == 1:
        return bool(
            re.search(
                r"\b" + re.escape(term) + r"\b",
                text,
            )
        )

    return False


def match_terms(terms, resume_text):
    terms = clean_list(terms)

    matched = []
    missing = []

    for term in terms:
        if term_exists(term, resume_text):
            matched.append(term)
        else:
            missing.append(term)

    return matched, missing


def match_percentage(terms, resume_text):
    terms = clean_list(terms)

    if not terms:
        return 100.0

    matched, _ = match_terms(
        terms,
        resume_text,
    )

    return round(
        (len(matched) / len(terms)) * 100,
        2,
    )

def extract_resume(state: JobAgentState):

    reader = PdfReader(
        state["resume_path"]
    )

    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text_parts.append(page_text)

    state["resume_text"] = "\n".join(
        text_parts
    ).strip()

    print("\nResume extracted successfully.")
    print(
        "Resume characters:",
        len(state["resume_text"]),
    )

    return state

def analyze_resume(state: JobAgentState):

    prompt = f"""
You are an expert resume analyzer.

Analyze ONLY the following resume.

RESUME:
{state["resume_text"]}

Extract:

1. Most suitable job role
2. Technical skills
3. Experience
4. Education
5. Projects

Return ONLY valid JSON:

{{
    "job_role": "",
    "skills": "",
    "experience": "",
    "education": "",
    "projects": ""
}}

Rules:
- Do not invent information.
- Do not turn projects into professional employment.
- Keep answers concise.
- Do not use markdown.
"""

    try:
        response = model.invoke(prompt)

        data = parse_json_response(
            get_response_text(response)
        )

    except Exception as exc:
        print("Resume analysis error:", exc)
        data = {}

    state["job_role"] = str(
        data.get("job_role", "")
    ).strip()

    state["skills"] = str(
        data.get("skills", "")
    ).strip()

    state["experience"] = str(
        data.get("experience", "")
    ).strip()

    state["education"] = str(
        data.get("education", "")
    ).strip()

    state["projects"] = str(
        data.get("projects", "")
    ).strip()

    print("\n==============================")
    print("RESUME ANALYSIS")
    print("==============================")
    print("Job Role:", state["job_role"])
    print("Skills:", state["skills"])
    print("Experience:", state["experience"])
    print("Education:", state["education"])
    print("Projects:", state["projects"])

    return state

def search_jobs_node(state: JobAgentState):

    print("\n==============================")
    print("JOB SEARCH")
    print("==============================")

    job_role = state.get(
        "job_role",
        "",
    ).strip()

    if not job_role:
        print("Job role was not identified.")
        state["jobs"] = []
        return state

    print(
        "Searching jobs for:",
        job_role,
    )

    try:
        jobs = search_jobs(job_role)
    except Exception as exc:
        print("Job search error:", exc)
        jobs = []

    if not isinstance(jobs, list):
        jobs = []

    valid_jobs = []

    for job in jobs:

        if not isinstance(job, dict):
            continue

        job.setdefault("title", "Unknown Job")
        job.setdefault("company", "Unknown Company")
        job.setdefault("location", "India")
        job.setdefault("employment_type", "")
        job.setdefault("url", "")
        job.setdefault("description", "")

        job["ats_score"] = 0.0
        job["application_id"] = None
        job["application_status"] = "Pending Approval"

        valid_jobs.append(job)

    state["jobs"] = valid_jobs

    print(
        "\nTotal Jobs Found:",
        len(valid_jobs),
    )

    for index, job in enumerate(
        valid_jobs,
        start=1,
    ):
        print(
            f"{index}. "
            f"{job['title']} | "
            f"{job['company']} | "
            f"{job['location']}"
        )

    return state

def extract_job_requirements(job_description):

    if not job_description:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "keywords": [],
            "experience": [],
            "education": [],
            "job_role": [],
            "project_requirements": [],
        }

    prompt = f"""
You are an ATS requirement extraction system.

Analyze ONLY this job description.

JOB DESCRIPTION:
{job_description}

Extract explicitly mentioned requirements.

Return ONLY valid JSON:

{{
    "required_skills": [],
    "preferred_skills": [],
    "keywords": [],
    "experience": [],
    "education": [],
    "job_role": [],
    "project_requirements": []
}}

Rules:
- Do not invent requirements.
- Do not add common technologies unless explicitly mentioned.
- Keep each item short.
- Experience must contain explicit experience requirements.
- Education must contain explicit education requirements.
- Do not use markdown.
"""

    try:
        response = model.invoke(prompt)

        data = parse_json_response(
            get_response_text(response)
        )

    except Exception as exc:
        print(
            "Requirement extraction error:",
            exc,
        )
        data = {}

    keys = [
        "required_skills",
        "preferred_skills",
        "keywords",
        "experience",
        "education",
        "job_role",
        "project_requirements",
    ]

    for key in keys:
        data[key] = clean_list(
            data.get(key, [])
        )

    return data

def calculate_ats(state: JobAgentState):

    jobs = state.get("jobs", [])
    resume_text = state.get(
        "resume_text",
        "",
    )

    if not jobs:
        state["ats_score"] = 0.0
        state["ats_scores"] = []
        state["eligible_jobs"] = []
        state["current_job"] = {}
        state["job_description"] = ""
        return state

    print("\n" + "=" * 70)
    print("ATS ANALYSIS — EVERY JOB IS CHECKED INDEPENDENTLY")
    print("=" * 70)

    scored_jobs = []

    for index, job in enumerate(
        jobs,
        start=1,
    ):

        title = str(
            job.get(
                "title",
                "Unknown Job",
            )
        )

        company = str(
            job.get(
                "company",
                "Unknown Company",
            )
        )

        location = str(
            job.get(
                "location",
                "",
            )
        )

        description = str(
            job.get(
                "description",
                "",
            )
        )

        print("\n" + "-" * 70)
        print(
            f"ATS CHECK {index}/{len(jobs)}"
        )
        print("Job:", title)
        print("Company:", company)
        print("Location:", location)


        if not description.strip():

            job["ats_score"] = 0.0
            job["skill_score"] = 0.0
            job["keyword_score"] = 0.0
            job["experience_score"] = 0.0
            job["role_score"] = 0.0
            job["education_score"] = 0.0
            job["project_score"] = 0.0

            job["matched_skills"] = []
            job["missing_skills"] = []

            job["ats_reason"] = (
                "Job description was not available."
            )

            job["eligibility"] = "Review Match"
            job["application_status"] = (
                "Pending Approval"
            )

            scored_jobs.append(job)

            print("ATS Score: 0%")
            continue


        requirements = (
            extract_job_requirements(
                description
            )
        )

        required_skills = requirements[
            "required_skills"
        ]

        preferred_skills = requirements[
            "preferred_skills"
        ]

        keywords = requirements[
            "keywords"
        ]
        experience_requirements = (requirements["experience"])
        education_requirements = (requirements["education"])
        role_requirements = requirements["job_role"]
        project_requirements = (requirements["project_requirements"])


        required_skill_match = (match_percentage(required_skills,resume_text,))
        preferred_skill_match = (match_percentage(preferred_skills,resume_text,))
        keyword_match = (match_percentage(keywords,resume_text,))
        experience_match = (match_percentage(experience_requirements,resume_text,))
        education_match = (match_percentage(education_requirements,resume_text,))
        role_match = (match_percentage(role_requirements,resume_text,))
        project_match = ( match_percentage(project_requirements, resume_text,))


        deterministic_score = round(
            (
                required_skill_match * 0.35
                + keyword_match * 0.20
                + experience_match * 0.15
                + role_match * 0.10
                + education_match * 0.05
                + project_match * 0.15
            ),
            2,
        )


        prompt = f"""
You are a strict ATS resume screening engine.

Evaluate the candidate against ONLY THIS JOB.

Do not use any other job.
Do not invent candidate experience.
Do not assume a project is professional employment.

CANDIDATE RESUME:
{resume_text}

JOB TITLE:
{title}

COMPANY:
{company}

LOCATION:
{location}

JOB DESCRIPTION:
{description}

EXPLICIT JOB REQUIREMENTS:

Required skills:
{required_skills}

Preferred skills:
{preferred_skills}

Keywords:
{keywords}

Experience:
{experience_requirements}

Education:
{education_requirements}

Role:
{role_requirements}

Project requirements:
{project_requirements}

DETERMINISTIC MATCH SIGNALS:

Required skills: {required_skill_match}
Preferred skills: {preferred_skill_match}
Keywords: {keyword_match}
Experience: {experience_match}
Education: {education_match}
Role: {role_match}
Projects: {project_match}

Baseline ATS score:
{deterministic_score}

SCORING WEIGHTS:

Skills       35%
Keywords     20%
Experience   15%
Role         10%
Education     5%
Projects     15%

IMPORTANT:
- Missing required skills should lower the score.
- Explicit professional experience requirements matter.
- Student/project experience must not be counted as professional employment.
- A job title match alone must not create a high score.
- 90+ means an exceptionally strong match.
- Score must be between 0 and 100.
- Evaluate this job independently.

Return ONLY JSON:

{{
    "ats_score": 0,
    "skill_score": 0,
    "keyword_score": 0,
    "experience_score": 0,
    "role_score": 0,
    "education_score": 0,
    "project_score": 0,
    "matched_skills": [],
    "missing_skills": [],
    "reason": ""
}}
"""

        try:

            response = model.invoke(prompt)

            data = parse_json_response(
                get_response_text(response)
            )

        except Exception as exc:

            print(
                f"ATS model error for {title}:",
                exc,
            )

            data = {}


        if "ats_score" in data:

            ai_score = safe_score(
                data.get(
                    "ats_score",
                    0,
                )
            )

            score = round(
                (
                    ai_score * 0.70
                    + deterministic_score * 0.30
                ),
                2,
            )

        else:

            score = deterministic_score

        score = safe_score(score)


        skill_score = safe_score(
            data.get(
                "skill_score",
                required_skill_match,
            )
        )

        keyword_score = safe_score(
            data.get(
                "keyword_score",
                keyword_match,
            )
        )

        experience_score = safe_score(
            data.get(
                "experience_score",
                experience_match,
            )
        )

        role_score = safe_score(
            data.get(
                "role_score",
                role_match,
            )
        )

        education_score = safe_score(
            data.get(
                "education_score",
                education_match,
            )
        )

        project_score = safe_score(
            data.get(
                "project_score",
                project_match,
            )
        )

        matched_skills = clean_list(
            data.get(
                "matched_skills",
                [],
            )
        )

        missing_skills = clean_list(
            data.get(
                "missing_skills",
                [],
            )
        )
        if not matched_skills:

            matched_skills, _ = match_terms(
                required_skills + preferred_skills,
                resume_text,
            )

        if not missing_skills:

            _, missing_skills = match_terms(
                required_skills,
                resume_text,
            )

        reason = str(
            data.get(
                "reason",
                "",
            )
        ).strip()

        if not reason:

            reason = (
                f"ATS score is {score}%. "
                f"Required-skill match is "
                f"{required_skill_match}%, "
                f"keyword match is {keyword_match}%, "
                f"and experience match is "
                f"{experience_match}%."
            )


        job["ats_score"] = score

        job["skill_score"] = skill_score
        job["keyword_score"] = keyword_score
        job["experience_score"] = experience_score
        job["role_score"] = role_score
        job["education_score"] = education_score
        job["project_score"] = project_score

        job["matched_skills"] = matched_skills
        job["missing_skills"] = missing_skills

        job["ats_reason"] = reason
        if score >= ATS_THRESHOLD:
            job["eligibility"] = "Eligible"
        else:
            job["eligibility"] = "Review Match"

        job["application_status"] = (
            "Pending Approval"
        )

        job["application_id"] = None
        scored_jobs.append(job)
        print(f"ATS SCORE: {score}%")
        print("Eligibility:",job["eligibility"],)
        print( "Matched Skills:", matched_skills,)
        print("Missing Skills:",missing_skills,)

    scored_jobs.sort(
        key=lambda job: safe_score(
            job.get(
                "ats_score",
                0,
            )
        ),
        reverse=True,
    )

    state["jobs"] = scored_jobs

    state["ats_scores"] = [
        safe_score(
            job.get(
                "ats_score",
                0,
            )
        )
        for job in scored_jobs
    ]

    state["eligible_jobs"] = list(
        scored_jobs
    )
    if scored_jobs:

        best_job = scored_jobs[0]

        state["current_job"] = best_job

        state["ats_score"] = safe_score(
            best_job.get(
                "ats_score",
                0,
            )
        )

        state["job_description"] = (
            best_job.get(
                "description",
                "",
            )
        )

    else:

        state["current_job"] = {}
        state["ats_score"] = 0.0
        state["job_description"] = ""

    print("\n" + "=" * 70)
    print("FINAL ATS RESULTS — ALL JOBS")
    print("=" * 70)

    for rank, job in enumerate(scored_jobs,start=1):
        print(
            f"{rank}. "
            f"{job.get('title', '')} | "
            f"{job.get('company', '')} | "
            f"ATS: {job.get('ats_score', 0)}% | "
            f"{job.get('eligibility', '')}"
        )

    strong_matches = len([
        job
        for job in scored_jobs
        if safe_score(
            job.get(
                "ats_score",
                0,
            )
        ) >= ATS_THRESHOLD
    ])

    print("=" * 70)
    print(
        "Total Jobs Checked:",
        len(scored_jobs),
    )
    print(
        "Strong Matches (70%+):",
        strong_matches,
    )
    print(
        "Jobs Available For Human Review:",
        len(scored_jobs),
    )

    return state

def improvement_resume(state: JobAgentState):

    job = state.get(
        "current_job",
        {},
    )

    prompt = f"""
You are a professional resume improvement expert.

RESUME:
{state.get("resume_text", "")}

BEST MATCHING JOB:
{job.get("description", "")}

ATS SCORE:
{state.get("ats_score", 0)}

MISSING SKILLS:
{job.get("missing_skills", [])}

Give 4-5 practical improvements.

Focus on:
- Missing skills
- Missing keywords
- Projects
- Experience
- Job-specific improvements

Do not rewrite the entire resume.
Do not invent experience.
"""

    try:

        response = model.invoke(prompt)

        state["improvement"] = (
            get_response_text(response)
        )

    except Exception as exc:

        print(
            "Resume improvement error:",
            exc,
        )

        state["improvement"] = ""

    return state


def ats_decision(state: JobAgentState):

    if not state.get("jobs"):
        return "NoJobs"

    return "JobsFound"

def prepare_for_approval(state: JobAgentState,):
    jobs = state.get("jobs",[])
    for job in jobs:

        score = safe_score(
            job.get(
                "ats_score",
                0,
            )
        )

        if score >= ATS_THRESHOLD:
            job["eligibility"] = "Eligible"
        else:
            job["eligibility"] = "Review Match"

        job["application_status"] = (
            "Pending Approval"
        )

    state["eligible_jobs"] = list(jobs)

    state["approval_status"] = (
        "PENDING_APPROVAL"
    )

    state["application_status"] = (
        "Pending Approval"
    )

    print("\n" + "=" * 70)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 70)

    print(
        "Jobs available for approval:",
        len(jobs),
    )

    for index, job in enumerate(
        jobs,
        start=1,
    ):

        print(
            f"{index}. "
            f"{job.get('title', '')} | "
            f"{job.get('company', '')} | "
            f"ATS: {job.get('ats_score', 0)}% | "
            f"{job.get('eligibility', '')}"
        )

    print(
        "\nAI recommends/ranks."
        "\nHuman decides."
    )

    return state



def create_pending_application(state: JobAgentState,):
    jobs = state.get(
        "eligible_jobs",
        [],
    )

    application_ids = []

    if not jobs:

        state["application_ids"] = []

        print(
            "\nNo jobs available for application tracking."
        )

        return state

    print("\n" + "=" * 70)
    print("CREATING APPLICATION TRACKING RECORDS")
    print("=" * 70)

    for index, job in enumerate(
        jobs,
        start=1,
    ):

        try:
            existing_id = job.get(
                "application_id"
            )

            if existing_id:

                application_ids.append(
                    existing_id
                )

                continue

            application_id = save_application(

                company=job.get(
                    "company",
                    "",
                ),

                job_title=job.get(
                    "title",
                    "",
                ),

                location=job.get(
                    "location",
                    "",
                ),

                job_url=job.get(
                    "url",
                    "",
                ),

                ats_score=safe_score(
                    job.get(
                        "ats_score",
                        0,
                    )
                ),
            )

      
            job["application_id"] = (
                application_id
            )

            job["application_status"] = (
                "Pending Approval"
            )

            application_ids.append(
                application_id
            )

            print(
                f"{index}. "
                f"{job.get('title', '')} | "
                f"{job.get('company', '')} | "
                f"ATS: {job.get('ats_score', 0)}% | "
                f"DB ID: {application_id}"
            )

        except Exception as exc:

            print(
                f"Database error for "
                f"{job.get('title', '')}:",
                exc,
            )

            job["application_id"] = None

    state["application_ids"] = (
        application_ids
    )

    if jobs:

        state["current_job"] = jobs[0]

        state["application_id"] = (
            jobs[0].get(
                "application_id",
                0,
            )
        )

    print(
        "\nTotal application records:",
        len(application_ids),
    )
    
    print(
        "No application was submitted automatically."
    )

    return state


graph = StateGraph(JobAgentState)

graph.add_node("extract_resume",extract_resume,)
graph.add_node("analyze_resume",analyze_resume,)
graph.add_node("search_jobs",search_jobs_node,)
graph.add_node("calculate_ats",calculate_ats,)
graph.add_node("improvement_resume",improvement_resume,)
graph.add_node("prepare_for_approval",prepare_for_approval,)
graph.add_node("create_pending_application",create_pending_application,)


graph.add_edge(START,"extract_resume",)
graph.add_edge( "extract_resume", "analyze_resume",)
graph.add_edge("analyze_resume","search_jobs",)
graph.add_edge("search_jobs","calculate_ats",)
graph.add_conditional_edges("calculate_ats",ats_decision,
    {
        "JobsFound":
            "prepare_for_approval",

        "NoJobs":
            END,
    },)
graph.add_edge("prepare_for_approval","create_pending_application",)
graph.add_edge("create_pending_application",END,)


workflow = graph.compile()
