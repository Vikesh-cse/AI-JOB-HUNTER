import os
import requests
from dotenv import load_dotenv

load_dotenv()


def search_jobs(job_role):

    print("\n==============================")
    print("JOB SEARCH API")
    print("==============================")

    print("Job role received:", repr(job_role))


    if not job_role:

        print("❌ Job role is empty.")

        return []


    url = "https://jsearch.p.rapidapi.com/search-v2"


    querystring = {
        "query": job_role,
        "num_pages": "1",
        "country": "India",
        "language": "English",
        "date_posted": "month"
    }


    headers = {
        "x-rapidapi-key": os.getenv(
            "RAPIDAPI_KEY"
        ),

        "x-rapidapi-host":
            "jsearch.p.rapidapi.com",

        "Content-Type":
            "application/json"
    }


    try:

        response = requests.get(
            url,
            headers=headers,
            params=querystring,
            timeout=30
        )

    except requests.RequestException as e:

        print(
            "❌ API Request Error:",
            e
        )

        return []


    print(
        "API Status:",
        response.status_code
    )


    if response.status_code != 200:

        print(
            "❌ API Error:",
            response.text
        )

        return []



    try:

        data = response.json()

    except ValueError:

        print(
            "❌ API did not return JSON."
        )

        return []


    api_data = data.get(
        "data",
        {}
    )


    if not isinstance(
        api_data,
        dict
    ):

        print(
            "❌ Unexpected API data format."
        )

        return []


    jobs = api_data.get(
        "jobs",
        []
    )



    if not isinstance(
        jobs,
        list
    ):

        print(
            "❌ Jobs is not a list:",
            type(jobs)
        )

        return []


    print(
        "Jobs received from API:",
        len(jobs)
    )



    job_list = []


    for job in jobs:

        if not isinstance(
            job,
            dict
        ):
            continue


        job_list.append({

            "title": job.get(
                "job_title",
                ""
            ),

            "company": job.get(
                "employer_name",
                ""
            ),

            "location": job.get(
                "job_location",
                ""
            ),

            "description": job.get(
                "job_description",
                ""
            ),

            "url": job.get(
                "job_apply_link",
                ""
            ),

            "employment_type": job.get(
                "job_employment_type",
                ""
            )
        })


    print(
        "Clean jobs:",
        len(job_list)
    )



    return job_list