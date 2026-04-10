from fastapi import APIRouter
from app.db.database import get_connection
from datetime import datetime

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/summary")
def get_dashboard_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM schedules")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as scheduled FROM schedules WHERE status = 'scheduled'")
    scheduled = cursor.fetchone()["scheduled"]

    cursor.execute("SELECT COUNT(*) as completed FROM schedules WHERE status = 'completed'")
    completed = cursor.fetchone()["completed"]

    cursor.execute("SELECT COUNT(*) as cancelled FROM schedules WHERE status = 'cancelled'")
    cancelled = cursor.fetchone()["cancelled"]

    conn.close()

    return {
        "total_interviews": total,
        "scheduled_interviews": scheduled,
        "completed_interviews": completed,
        "cancelled_interviews": cancelled
    }


@router.get("/dashboard/upcoming")
def get_upcoming_interviews():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM schedules
        WHERE status = 'scheduled'
        ORDER BY interview_date ASC, interview_time ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@router.get("/dashboard/completed")
def get_completed_interviews():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM schedules
        WHERE status = 'completed'
        ORDER BY interview_date DESC, interview_time DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]