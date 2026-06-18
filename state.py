# state.py
# Shared state schema for the ColdIQ pipeline
# This is the "whiteboard" every agent reads from and writes to

from typing import TypedDict

class ColdIQState(TypedDict):
    # Job listing information
    job_title: str               # e.g. "Machine Learning Engineer"
    company_name: str            # e.g. "Acme Corp"
    job_description: str         # full job posting text
    required_skills: list[str]   # e.g. ["Python", "LangChain", "SQL"]

    # Qualifier agent outputs
    qualifier_score: int         # 0-100 match score
    qualifier_reasoning: str     # explanation of score and what to emphasize

    # Finder agent outputs
    hiring_manager_name: str     # e.g. "Jane Smith"
    hiring_manager_title: str    # e.g. "Engineering Manager"
    hiring_manager_linkedin: str # e.g. "linkedin.com/in/janesmith"
    hiring_manager_email: str    # manually provided by you

    # Drafter agent outputs
    draft_email: str             # the generated email

    # Reviewer agent outputs
    review_feedback: str         # critique if rejected
    approved: bool               # True = send, False = loop back to drafter
    review_loops: int            # tracks how many revision cycles have happened

    # Application log data
    date_applied: str            # timestamp of when email was sent
    outcome: str                 # "sent", "responded", "no response" etc