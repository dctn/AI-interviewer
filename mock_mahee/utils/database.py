"""
Database utility for auto-scheduling candidates.
This module was referenced in the original shortlisting views but did not exist
in the codebase. It is preserved here as a stub for future implementation.
"""
from datetime import datetime, timedelta


def auto_schedule_candidate_direct(candidate_name, email, role):
    """
    Auto-schedule a candidate after shortlisting.
    
    Uses the Schedule model to create a new interview slot.
    """
    from mock_mahee.models import Schedule

    total_schedules = Schedule.objects.count()
    slots_per_day = 8
    slot_duration_minutes = 30
    start_hour = 10
    start_minute = 0

    day_offset = total_schedules // slots_per_day
    slot_index = total_schedules % slots_per_day

    base_date = datetime.now().date() + timedelta(days=1 + day_offset)

    slot_start_time = datetime.combine(base_date, datetime.min.time()).replace(
        hour=start_hour, minute=start_minute
    ) + timedelta(minutes=slot_index * slot_duration_minutes)

    schedule = Schedule.objects.create(
        candidate_name=candidate_name,
        email=email,
        role=role,
        interview_date=slot_start_time.strftime('%Y-%m-%d'),
        interview_time=slot_start_time.strftime('%I:%M %p'),
        status='scheduled'
    )

    return {
        'id': schedule.id,
        'candidate_name': schedule.candidate_name,
        'email': schedule.email,
        'role': schedule.role,
        'interview_date': schedule.interview_date,
        'interview_time': schedule.interview_time,
        'status': schedule.status
    }
