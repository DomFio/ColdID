# agents/reviewer.py
# Reviewer Agent - fourth and final agent in the ColdIQ pipeline
# Critiques the drafted email against the job listing and applicant info
# Either approves the email and triggers sending, or rejects it with feedback
# Rejected drafts loop back to the drafter for revision
# Tracks review loop count to prevent infinite loops

from langchain_google_genai import ChatGoogleGenerativeAI
from config import LLM_MODEL, MAX_REVIEW_LOOPS
from state import ColdIQState

def reviewer_agent(state: ColdIQState) -> dict:
    """
    Reviews the draft email against a strict rubric.
    Returns approved=True if it passes, approved=False with feedback if it fails.
    Stops looping if MAX_REVIEW_LOOPS is reached.
    """

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL)

    # If we've hit the loop limit, force approve to prevent infinite loops
    if state.get('review_loops', 0) >= MAX_REVIEW_LOOPS:
        return {
            "approved": True,
            "review_feedback": "Max review loops reached - sending best available draft"
        }

    prompt = f"""
    You are a strict email reviewer. Your job is to critique a cold job application 
    email and decide if it is ready to send.

    Job Title: {state['job_title']}
    Company: {state['company_name']}
    Job Description: {state['job_description']}

    Hiring Manager: {state['hiring_manager_name']}
    Hiring Manager Title: {state['hiring_manager_title']}

    Qualifier Reasoning (what should be emphasized):
    {state['qualifier_reasoning']}

    Draft Email:
    {state['draft_email']}

    Review the email against this rubric:
    - Is it under 200 words?
    - Does it open with a specific personalized line?
    - Does it reference specific projects or technologies by name?
    - Does it highlight the strongest matches from the qualifier reasoning?
    - Does it avoid generic phrases like "I am passionate" or "I am a quick learner"?
    - Does it end with a clear call to action?
    - Does it sound like a real person wrote it, not an AI?

    If it passes all criteria respond in this exact format:
    APPROVED: yes
    FEEDBACK: none

    If it fails any criteria respond in this exact format:
    APPROVED: no
    FEEDBACK: <specific actionable feedback on exactly what to fix>
    """

    response = llm.invoke(prompt)

    # Parse the response
    lines = response.content.strip().split("\n")
    approved = lines[0].replace("APPROVED:", "").strip().lower() == "yes"
    feedback = lines[1].replace("FEEDBACK:", "").strip()

    # Increment the review loop counter
    current_loops = state.get('review_loops', 0)

    return {
        "approved": approved,
        "review_feedback": feedback,
        "review_loops": current_loops + 1
    }