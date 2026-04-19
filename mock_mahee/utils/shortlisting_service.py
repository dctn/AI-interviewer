"""
Shortlisting service stub.
This module was referenced in the original shortlisting views but did not exist
in the codebase. It is preserved here as a stub for future implementation.
"""


def perform_shortlisting(resume_analysis, role, job_description):
    """
    Perform AI-based shortlisting of a candidate.
    
    TODO: Implement actual shortlisting logic with Groq/LLM.
    Currently returns a placeholder response.
    """
    return {
        'candidate_name': resume_analysis.get('name', 'Unknown'),
        'email': resume_analysis.get('email', ''),
        'role': role,
        'shortlist_status': 'pending',
        'score': 0.0,
        'matching_skills': [],
        'missing_skills': [],
        'feedback': 'Shortlisting service not yet implemented.'
    }
