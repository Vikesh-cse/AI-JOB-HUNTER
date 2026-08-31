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

            created_date TEXT,

            approved_date TEXT,

            applied_date TEXT,

            interview_date TEXT,

            last_updated TEXT,

            notes TEXT,

            rejection_reason TEXT
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

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO applications
        (
            company,
            job_title,
            location,
            job_url,
            ats_score,
            status,
            created_date,
            approved_date,
            applied_date,
            interview_date,
            last_updated,
            notes,
            rejection_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        company,

        job_title,

        location,

        job_url,

        ats_score,

        "Pending Approval",

        current_time,

        None,

        None,

        None,

        current_time,

        "",

        ""
    ))

    application_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return application_id


def update_status(
    application_id,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE applications

        SET
            status = ?,
            last_updated = ?

        WHERE id = ?
    """, (

        status,

        current_time,

        application_id
    ))

    if status == "Approved":

        cursor.execute("""
            UPDATE applications

            SET approved_date = ?

            WHERE id = ?
        """, (

            current_time,

            application_id
        ))

    elif status == "Applied":

        cursor.execute("""
            UPDATE applications

            SET applied_date = ?

            WHERE id = ?
        """, (

            current_time,

            application_id
        ))

    elif status == "Interview":

        cursor.execute("""
            UPDATE applications

            SET interview_date = ?

            WHERE id = ?
        """, (

            current_time,

            application_id
        ))

    connection.commit()

    connection.close()


def reject_application(
    application_id,
    reason=""
):

    connection = get_connection()

    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE applications

        SET
            status = ?,
            rejection_reason = ?,
            last_updated = ?

        WHERE id = ?
    """, (

        "Rejected",

        reason,

        current_time,

        application_id
    ))

    connection.commit()

    connection.close()

def update_notes(
    application_id,
    notes
):

    connection = get_connection()

    cursor = connection.cursor()

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        UPDATE applications

        SET
            notes = ?,
            last_updated = ?

        WHERE id = ?
    """, (

        notes,

        current_time,

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
            created_date,
            approved_date,
            applied_date,
            interview_date,
            last_updated,
            notes,
            rejection_reason

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
        SELECT
            id,
            company,
            job_title,
            location,
            job_url,
            ats_score,
            status,
            created_date,
            approved_date,
            applied_date,
            interview_date,
            last_updated,
            notes,
            rejection_reason

        FROM applications

        WHERE id = ?
    """, (

        application_id,
    ))

    application = cursor.fetchone()

    connection.close()

    return application

def get_applications_by_status(
    status
):

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
            created_date,
            approved_date,
            applied_date,
            interview_date,
            last_updated,
            notes,
            rejection_reason

        FROM applications

        WHERE status = ?

        ORDER BY id DESC
    """, (

        status,
    ))

    applications = cursor.fetchall()

    connection.close()

    return applications

if __name__ == "__main__":

    create_table()

    print(
        "Database created successfully!"
    )