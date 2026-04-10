from fastapi import APIRouter, HTTPException
from app.schemas.shortlist import ShortlistRequest, ShortlistResponse
from app.services.shortlisting_service import perform_shortlisting
from app.integrations.interview_management_client import call_auto_schedule

router = APIRouter(tags=["Shortlisting"])


@router.post("/shortlist", response_model=ShortlistResponse)
def shortlist_candidate(payload: ShortlistRequest):
    try:
        result = perform_shortlisting(
            resume_analysis=payload.resume_analysis,
            role=payload.role,
            job_description=payload.job_description
        )

        if result["shortlist_status"] == "shortlisted":
            schedule_result = call_auto_schedule(
                candidate_name=result["candidate_name"],
                email=result["email"],
                role=result["role"]
            )
            result["schedule"] = schedule_result
        else:
            result["schedule"] = None

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))