import json
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from job_search import search_jobs
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from pypdf import PdfReader
from dotenv import load_dotenv


load_dotenv()


class JobAgentState(TypedDict):

    resume_path: str
    resume_text: str
    job_role: str
    skills: str
    experience: str
    education: str
    projects: str
    jobs: list
    job_description: str
    ats_score: float
    improvement: str

import os

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if api_key:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0
        )
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0
    )



def get_response_text(response):

    content = response.content
    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text = ""

        for item in content:

            if isinstance(item, str):
                text += item

            elif isinstance(item, dict):

                if "text" in item:
                    text += str(item["text"])

        return text

    return str(content)


def extract_resume(state: JobAgentState):

    reader = PdfReader(
        state["resume_path"]
    )

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    state["resume_text"] = text

    print("\nResume extracted successfully.")

    return state


def analyze_resume(state: JobAgentState):

    prompt = f"""
You are an expert resume analyzer and job role identifier.

Analyze this resume:

{state["resume_text"]}

Extract:

1. Most suitable job role
2. Technical skills
3. Experience
4. Education
5. Projects

Return ONLY valid JSON.

Use exactly this structure:

{{
    "job_role": "most suitable job role",
    "skills": "technical skills",
    "experience": "experience",
    "education": "education",
    "projects": "projects"
}}

Rules:

- Do not use markdown.
- Do not use ```json.
- Do not invent information.
- Keep answers short and accurate.
"""

    model = get_llm()
    response = model.invoke(prompt)

    result = get_response_text(response)

    result = result.strip()

    result = re.sub(
        r"```json",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"```",
        "",
        result
    )

    result = result.strip()


    try:

        data = json.loads(result)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            result,
            re.DOTALL
        )

        if match:

            try:
                data = json.loads(
                    match.group()
                )

            except json.JSONDecodeError:
                data = {}

        else:
            data = {}


    state["job_role"] = str(
        data.get("job_role", "")
    )

    state["skills"] = str(
        data.get("skills", "")
    )

    state["experience"] = str(
        data.get("experience", "")
    )

    state["education"] = str(
        data.get("education", "")
    )

    state["projects"] = str(
        data.get("projects", "")
    )


    print("\n==============================")
    print("RESUME ANALYSIS")
    print("==============================")

    print(
        "Job Role:",
        state["job_role"]
    )

    print(
        "Skills:",
        state["skills"]
    )

    print(
        "Experience:",
        state["experience"]
    )

    print(
        "Education:",
        state["education"]
    )

    print(
        "Projects:",
        state["projects"]
    )

    return state


def search_jobs_node(state: JobAgentState):

    print("\n==============================")
    print("JOB SEARCH")
    print("==============================")


    job_role = state["job_role"].strip()



    if not job_role:

        print(
            "Job role was not identified."
        )

        state["jobs"] = []

        return state


    print(
        "Searching jobs for:",
        job_role
    )


    jobs = search_jobs(
        job_role
    )


    state["jobs"] = jobs


    print(
        "\nTotal Jobs Found:",
        len(jobs)
    )


    for index, job in enumerate(
        jobs,
        start=1
    ):

        print(
            "\n------------------------------"
        )

        print(
            f"{index}. {job['title']}"
        )

        print(
            "Company:",
            job["company"]
        )

        print(
            "Location:",
            job["location"]
        )

        print(
            "Type:",
            job["employment_type"]
        )

        print(
            "Apply:",
            job["url"]
        )


    return state



def calculate_ats(state: JobAgentState):

    if not state["jobs"]:

        state["ats_score"] = 0.0
        state["job_description"] = ""

        return state

    job = state["jobs"][0]


    state["job_description"] = job[
        "description"
    ]


    prompt = f"""
You are an ATS resume evaluator.

Compare this resume with the job description.

RESUME:

{state["resume_text"]}


JOB DESCRIPTION:

{state["job_description"]}


Evaluate:

1. Skills match
2. Keywords match
3. Experience match
4. Job role match
5. Education match
6. Project relevance

Give one final ATS score between 0 and 100.

Return ONLY the number.

Example:

78
"""


    model = get_llm()
    response = model.invoke(prompt)


    result = get_response_text(
        response
    ).strip()

    match = re.search(
        r"\b(?:100|[1-9]?\d(?:\.\d+)?)\b",
        result
    )


    if match:

        score = float(
            match.group()
        )

    else:

        score = 0.0


    score = max(
        0.0,
        min(score, 100.0)
    )


    state["ats_score"] = score


    print(
        "\nATS Score:",
        score
    )


    return state


def improvement_resume(state: JobAgentState):

    prompt = f"""
You are a professional resume improvement expert.

RESUME:

{state["resume_text"]}


JOB DESCRIPTION:

{state["job_description"]}


ATS SCORE:

{state["ats_score"]}


The ATS score is below 70.

Give 4-5 practical improvements.

Focus on:

- Missing skills
- Missing keywords
- Projects
- Experience
- Job-specific improvements

Do not rewrite the entire resume.

Give only useful suggestions.
"""


    model = get_llm()
    response = model.invoke(
        prompt
    )


    state["improvement"] = (
        get_response_text(response)
    )

    return state


def ats_decision(state: JobAgentState):

    if state["ats_score"] >= 70:

        return "Good"

    return "Improvement"

graph = StateGraph(JobAgentState)

graph.add_node("extract_resume",extract_resume)
graph.add_node("analyze_resume",analyze_resume)
graph.add_node("search_jobs",search_jobs_node)
graph.add_node("calculate_ats",calculate_ats)
graph.add_node("improvement_resume",improvement_resume)


graph.add_edge(START,"extract_resume")
graph.add_edge("extract_resume","analyze_resume")
graph.add_edge("analyze_resume","search_jobs")
graph.add_edge("search_jobs","calculate_ats")
graph.add_conditional_edges( "calculate_ats",ats_decision,{
        "Good": END,
        "Improvement": "improvement_resume"
    }
)
graph.add_edge("improvement_resume",END)

workflow = graph.compile()