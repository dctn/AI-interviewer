from fastapi import APIRouter, HTTPException
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.db.database import get_connection
from datetime import datetime, timedelta

router = APIRouter(tags=["Schedules"])


# -----------------------------
# Manual Schedule Create
# -----------------------------
@router.post("/schedules")
def create_schedule(payload: ScheduleCreate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO schedules (candidate_name, email, role, interview_date, interview_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        payload.candidate_name,
        payload.email,
        payload.role,
        payload.interview_date,
        payload.interview_time,
        payload.status
    ))

    conn.commit()
    schedule_id = cursor.lastrowid

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row)


# -----------------------------
# Auto Scheduling Logic
# -----------------------------
@router.post("/auto-schedule")
def auto_schedule_candidate(payload: ScheduleCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # Count total already scheduled candidates
    cursor.execute("SELECT COUNT(*) as total FROM schedules")
    total_schedules = cursor.fetchone()["total"]

    slots_per_day = 8
    slot_duration_minutes = 30
    start_hour = 10
    start_minute = 0

    day_offset = total_schedules // slots_per_day
    slot_index = total_schedules % slots_per_day

    base_date = datetime.now().date() + timedelta(days=1 + day_offset)

    slot_start_time = datetime.combine(base_date, datetime.min.time()).replace(
        hour=start_hour,
        minute=start_minute
    ) + timedelta(minutes=slot_index * slot_duration_minutes)

    interview_date = slot_start_time.strftime("%Y-%m-%d")
    interview_time = slot_start_time.strftime("%I:%M %p")

    cursor.execute("""
        INSERT INTO schedules (candidate_name, email, role, interview_date, interview_time, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        payload.candidate_name,
        payload.email,
        payload.role,
        interview_date,
        interview_time,
        "scheduled"
    ))

    conn.commit()
    schedule_id = cursor.lastrowid

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    row = cursor.fetchone()
    conn.close()

    return {
        "message": "Candidate auto-scheduled successfully",
        "schedule": dict(row)
    }


# -----------------------------
# Get All Schedules
# -----------------------------
@router.get("/schedules")
def get_all_schedules():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM schedules ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# -----------------------------
# Get Schedule By ID
# -----------------------------
@router.get("/schedules/{schedule_id}")
def get_schedule_by_id(schedule_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return dict(row)


# -----------------------------
# Update Schedule
# -----------------------------
@router.put("/schedules/{schedule_id}")
def update_schedule(schedule_id: int, payload: ScheduleUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Schedule not found")

    updated_candidate_name = payload.candidate_name if payload.candidate_name is not None else existing["candidate_name"]
    updated_email = payload.email if payload.email is not None else existing["email"]
    updated_role = payload.role if payload.role is not None else existing["role"]
    updated_interview_date = payload.interview_date if payload.interview_date is not None else existing["interview_date"]
    updated_interview_time = payload.interview_time if payload.interview_time is not None else existing["interview_time"]
    updated_status = payload.status if payload.status is not None else existing["status"]

    cursor.execute("""
        UPDATE schedules
        SET candidate_name = ?, email = ?, role = ?, interview_date = ?, interview_time = ?, status = ?
        WHERE id = ?
    """, (
        updated_candidate_name,
        updated_email,
        updated_role,
        updated_interview_date,
        updated_interview_time,
        updated_status,
        schedule_id
    ))

    conn.commit()

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return dict(updated_row)