import sqlite3
from datetime import datetime


DB_NAME = "applications.db"


def get_connection():

    return sqlite3.connect(DB_NAME)



def create_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT,

            job_title TEXT,

            location TEXT,

            job_url TEXT,

            ats_score REAL,

            status TEXT,

            applied_date TEXT
        )
    """)

    connection.commit()

    connection.close()



def save_application(
    company,
    job_title,
    location,
    job_url,
    ats_score
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO applications
        (
            company,
            job_title,
            location,
            job_url,
            ats_score,
            status,
            applied_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        company,
        job_title,
        location,
        job_url,
        ats_score,
        "Applied",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()

    connection.close()



def update_status(
    application_id,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE applications

        SET status = ?

        WHERE id = ?
    """, (
        status,
        application_id
    ))

    connection.commit()

    connection.close()




def get_applications():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            company,
            job_title,
            location,
            job_url,
            ats_score,
            status,
            applied_date

        FROM applications

        ORDER BY id DESC
    """)

    applications = cursor.fetchall()

    connection.close()

    return applications



def get_application(
    application_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM applications
        WHERE id = ?
    """, (
        application_id,
    ))

    application = cursor.fetchone()

    connection.close()

    return application



if __name__ == "__main__":

    create_table()

    print(
        "Database created successfully!"
    )