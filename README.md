# 🎯 AI Job Hunter — Intelligent Job Search & Application Tracker

An AI-powered job hunting system that analyzes a candidate's resume, searches for relevant jobs, evaluates each job using ATS-style matching, and provides a human-in-the-loop application workflow.

The system is built using **Python, Streamlit, LangChain, LangGraph, Gemini, PDF processing, and a database**.

---

## 🚀 Features

### 📄 1. Resume Analysis

Upload your resume in PDF format and let the AI extract:

* Target job role
* Technical skills
* Experience
* Education
* Projects

The resume is processed before job matching.

---

### 🔎 2. AI Job Search

The system searches for jobs based on the candidate's most suitable role.

Each job contains information such as:

* Job title
* Company
* Location
* Employment type
* Job URL
* Job description

---

### 🤖 3. ATS Resume Matching

Every discovered job is evaluated independently against the resume.

The system calculates an ATS-style score based on:

| Factor          | Weight |
| --------------- | -----: |
| Required Skills |    35% |
| Keywords        |    20% |
| Experience      |    15% |
| Role Match      |    10% |
| Education       |     5% |
| Projects        |    15% |

The system also identifies:

* ✅ Matched skills
* ❌ Missing skills
* 📊 ATS score
* 💡 Match explanation
* 📈 ATS component breakdown

---

### 🧠 4. AI + Deterministic ATS Evaluation

The project combines:

1. Deterministic keyword/requirement matching
2. LLM-based evaluation

This makes the ATS evaluation more robust than relying only on an LLM score.

Jobs are ranked according to their ATS score.

---

### 👤 5. Human-in-the-Loop Approval

The system does **not automatically apply** to jobs.

Every job goes through human approval.

```text
Job Found
    ↓
ATS Analysis
    ↓
Pending Approval
    ↓
Approve / Reject
    ↓
Approved
    ↓
Apply Now
    ↓
Applied
    ↓
Interview
    ↓
Hired / Rejected
```

This gives the candidate complete control over applications.

---

### 🚀 6. Application Tracking

Applications are stored in the database and can be tracked through different stages:

* Pending Approval
* Approved
* Applied
* Interview
* Rejected
* Hired

Each application has its own database ID.

---

### 📊 7. Dashboard

The dashboard provides an overview of:

* Jobs found
* Pending applications
* Approved applications
* Applied jobs
* Interviews
* Hired applications

---

### 🎨 8. Modern Streamlit UI

The application contains:

* Responsive job cards
* ATS score circles
* Match badges
* Skill pills
* Application status badges
* ATS breakdown charts
* Job descriptions
* Application timelines
* Sidebar navigation

---

# 🏗️ Project Architecture

```text
AI Job Hunter
│
├── app.py
│   └── Streamlit Frontend
│
├── agent.py
│   └── AI Job Hunting Workflow
│
├── job_search.py
│   └── Job Search
│
├── database.py
│   └── Application Database
│
├── temp_resume.pdf
│   └── Uploaded Resume
│
├── .env
│   └── API Keys
│
└── README.md
```

---

# 🔄 LangGraph Workflow

The backend uses LangGraph to organize the AI workflow.

```text
START
  │
  ▼
Extract Resume
  │
  ▼
Analyze Resume
  │
  ▼
Search Jobs
  │
  ▼
Calculate ATS
  │
  ├──────────────► No Jobs
  │                    │
  │                    ▼
  │                   END
  │
  ▼
Prepare Human Approval
  │
  ▼
Create Pending Applications
  │
  ▼
END
```

The important design principle is:

> **AI recommends. Human decides.**

---

# 🧰 Technologies Used

## Programming Language

* Python

## AI / LLM

* Google Gemini
* LangChain
* LangGraph

## Frontend

* Streamlit
* HTML
* CSS

## Resume Processing

* PyPDF

## Database

* SQLite / project database implementation

## Environment Management

* python-dotenv

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

Create a `requirements.txt` file containing:

```text
streamlit
langchain
langgraph
langchain-google-genai
python-dotenv
pypdf
```

Then run:

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

Do not upload `.env` to GitHub.

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
temp_resume.pdf
*.db
```

---

# ▶️ Run the Application

From the project directory:

```bash
streamlit run app.py
```

If Windows says:

```text
'streamlit' is not recognized as an internal or external command
```

use:

```bash
python -m streamlit run app.py
```

This is especially useful when Streamlit is installed inside your virtual environment.

---

# 🖥️ Application Pages

## 1. Dashboard

Provides an overview of your job search and application pipeline.

```text
Jobs Found
Pending
Approved
Applied
Interviews
Hired
```

---

## 2. Find Jobs

Upload your resume and start the AI job search.

```text
Upload Resume
      ↓
Analyze Resume
      ↓
Search Jobs
      ↓
ATS Analysis
      ↓
Display All Jobs
```

Every job is displayed with its ATS score.

---

## 3. Applications

Track your applications through the complete pipeline.

```text
Pending Approval
       ↓
Approved
       ↓
Applied
       ↓
Interview
       ↓
Hired
```

You can also reject an application.

---

## 4. Resume Analysis

Displays the AI's understanding of your resume:

* Target role
* Skills
* Experience
* Education
* Projects
* Best matching job
* ATS score
* Resume improvement suggestions

---

# 📋 Example Job Card

```text
┌──────────────────────────────────────────────┐
│ #1                                           │
│                                              │
│ AI Engineer                                  │
│ Example Company                              │
│ 📍 Bangalore · Full Time                     │
│                                              │
│                 ┌────────────┐               │
│                 │    87%     │               │
│                 │ ATS MATCH  │               │
│                 │Strong Match│               │
│                 └────────────┘               │
│                                              │
│ ✓ Eligible                                   │
│                                              │
│ [ View Job ↗ ]                               │
│                                              │
│ PENDING APPROVAL                             │
│                                              │
│ [ ✓ Approve ]       [ ✕ Reject ]             │
│                                              │
│ MATCHED SKILLS                               │
│ Python   LangChain   LLM   Git               │
│                                              │
│ MISSING SKILLS                               │
│ AWS                                         │
│                                              │
│ Why this matches:                            │
│ Strong alignment with the candidate profile. │
│                                              │
│ > View ATS Breakdown                         │
│ > View Job Description                       │
└──────────────────────────────────────────────┘
```

After approval:

```text
✓ APPROVED

[ View Job ↗ ]

[ 🚀 Apply Now ]
```

After applying:

```text
✓ APPLICATION SUBMITTED

[ 🎤 Mark Interview ]
```

---

# 🧠 ATS Scoring Logic

The system first extracts explicit requirements from each job description.

```text
Job Description
       ↓
Requirement Extraction
       ↓
Required Skills
Preferred Skills
Keywords
Experience
Education
Role
Projects
       ↓
Resume Matching
       ↓
Deterministic Score
       ↓
LLM Evaluation
       ↓
Final ATS Score
```

The final score combines AI evaluation with deterministic matching.

---

# 🔐 Human Approval Design

The application intentionally separates:

### Approval

```text
Pending Approval → Approved
```

from:

### Application

```text
Approved → Applied
```

This prevents the AI agent from silently submitting applications.

The user remains in control of the final decision.

---

# 📈 ATS Match Levels

|     Score | Match           |
| --------: | --------------- |
|   90–100% | Excellent Match |
|    80–89% | Strong Match    |
|    70–79% | Good Match      |
|    60–69% | Moderate Match  |
| Below 60% | Low Match       |

The 70% threshold is used as a recommendation/strong-match threshold. Jobs below 70% are still available for human review.

---

# 🗃️ Application Database

Each application is stored with information such as:

```text
Application ID
Company
Job Title
Location
Job URL
ATS Score
Status
Created Date
Approved Date
Applied Date
Interview Date
Last Updated
Notes
Rejection Reason
```

This allows the application tracker to maintain state even after the Streamlit page reruns.

---

# 🛡️ Important Design Principles

### 1. Every job is evaluated independently

The ATS system does not evaluate only the first job.

```python
for job in jobs:
    calculate_ats(job)
```

---

### 2. Projects are not treated as professional experience

The AI is instructed not to convert academic/project experience into professional employment.

---

### 3. Missing requirements reduce the match

Missing required skills and requirements can lower the ATS score.

---

### 4. Human approval is required

The AI recommends jobs but does not make the final application decision.

---

# 🚀 Future Improvements

Possible future features include:

* 🔗 LinkedIn job integration
* 🔗 Indeed integration
* 🌐 More job-search APIs
* 🤖 Browser-based application automation
* ✉️ AI-generated cover letters
* 📝 Job-specific resume customization
* 📧 Application email generation
* 🔔 Application reminders
* 📊 Advanced analytics
* 📈 Application success-rate tracking
* 🎯 Personalized job recommendations
* 🔍 Job deduplication
* 💾 Cloud database
* 🔐 User authentication
* 👥 Multi-user support

---

# ⚠️ Disclaimer

This project is an AI-assisted job search and application tracking system.

The ATS score is an **estimated compatibility score**, not an actual score generated by a company's Applicant Tracking System.

The current workflow requires human approval before an application is marked as applied.

Actual submission to external job websites requires a compatible API or browser automation integration.

---

# 👨‍💻 Project Structure

```text
.
├── app.py
├── agent.py
├── job_search.py
├── database.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# ⭐ Project Goal

The goal of **AI Job Hunter** is to combine:

```text
Generative AI
      +
Agentic AI
      +
LangGraph
      +
ATS Matching
      +
Job Search
      +
Human-in-the-Loop
      +
Application Tracking
```

into one intelligent career automation platform.

---

## 🎯 Core Philosophy

**Find → Analyze → Rank → Approve → Apply → Track**

> **AI recommends. You decide.**
> '''
> from pathlib import Path
> p = Path("/mnt/data/README.md")
> p.write_text(app_code, encoding="utf-8")
> print(f"Created {p} ({len(app_code.splitlines())} lines)")
> print("Syntax/content generation: OK")
