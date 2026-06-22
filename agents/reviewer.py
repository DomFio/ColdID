# agents/reviewer.py
# Reviewer Agent - fourth and final agent in the ColdIQ pipeline
# Critiques the drafted email against the job listing and applicant info
# Either approves the email and triggers sending, or rejects it with feedback
# Rejected drafts loop back to the drafter for revision
# Tracks review loop count to prevent infinite loops

from langchain_openai import ChatOpenAI
from config import LLM_MODEL, MAX_REVIEW_LOOPS
from state import ColdIQState

def reviewer_agent(state: ColdIQState) -> dict:
    """
    Reviews the draft email against a strict rubric.
    Returns approved=True if it passes, approved=False with feedback if it fails.
    Stops looping if MAX_REVIEW_LOOPS is reached.
    """

    # Initialize the LLM
    llm = ChatOpenAI(model=LLM_MODEL)

    # If we've hit the loop limit, force approve to prevent infinite loops
    if state.get('review_loops', 0) >= MAX_REVIEW_LOOPS:
        return {
            "approved": True,
            "review_feedback": "Max review loops reached - sending best available draft"
        }

    prompt = f"""
    You are a pragmatic email reviewer. Your job is to decide if a cold job 
    application email is ready to send. Be practical — a good email that 
    represents the candidate well should be approved. Do not reject based 
    on minor style preferences.

    Job Title: {state['job_title']}
    Company: {state['company_name']}
    Job Description: {state['job_description']}

    Hiring Manager: {state['hiring_manager_name']}
    Hiring Manager Title: {state['hiring_manager_title']}

    Qualifier Reasoning (what should be emphasized):
    {state['qualifier_reasoning']}

    Draft Email:
    {state['draft_email']}

    Review the email against this rubric. Be pragmatic — if the email is 
    genuinely good and ready to send, approve it. Minor style preferences 
    are NOT grounds for rejection. Only reject if there is a clear, 
    specific, fixable problem.

    Hard rejection criteria (ALL must pass or reject):
    - Is it under 250 words?
    - Does it reference at least one specific project or technology by name?
    - Does it end with a clear call to action?
    - Does it avoid obviously generic phrases like "I am passionate" or "I am a quick learner"?

    Soft criteria (nice to have, but NOT grounds for rejection alone):
    - Opens with a personalized line about the company
    - Highlights strongest matches from qualifier reasoning
    - Sounds conversational rather than formulaic

    If all hard criteria pass, APPROVE the email regardless of soft criteria.

    If it passes all criteria respond in this exact format:
    APPROVED: yes
    FEEDBACK: none

    If it fails any hard criteria respond in this exact format:
    APPROVED: no
    FEEDBACK: <specific actionable feedback on exactly what hard criterion failed and how to fix it>
    """

    response = llm.invoke(prompt)

    # Parse the response
    lines = response.content.strip().split("\n")
    approved = lines[0].replace("APPROVED:", "").strip().lower() == "yes"
    feedback = lines[1].replace("FEEDBACK:", "").strip()

    # Debug print so we can see why drafts are getting rejected
    print(f"\n--- REVIEW LOOP {state.get('review_loops', 0) + 1} ---")
    print(f"Approved: {approved}")
    print(f"Feedback: {feedback}\n")

    # Increment the review loop counter
    current_loops = state.get('review_loops', 0)

    return {
        "approved": approved,
        "review_feedback": feedback,
        "review_loops": current_loops + 1
    }