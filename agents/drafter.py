## agents/drafter.py
# Drafter Agent - third agent in the ColdIQ pipeline
# Takes job listing, qualifier reasoning, and hiring manager info from state
# Queries RAG system for relevant applicant experience
# Writes a personalized cold email grounded in real experience

from langchain_openai import ChatOpenAI
from config import LLM_MODEL
from state import ColdIQState
from rag import retrieve_context

def drafter_agent(state: ColdIQState) -> dict:
    """
    Uses the qualifier reasoning to know what to emphasize.
    Queries RAG for the most relevant projects and skills.
    Writes a personalized cold email to the hiring manager.
    """

    # Initialize the LLM
    llm = ChatOpenAI(model=LLM_MODEL)

    # Query the RAG system for relevant candidate experience
    query = f"{state['job_title']} {state['qualifier_reasoning']}"
    candidate_context = retrieve_context(query, k=4)

    # Prompt uses everything accumulated in state so far
    prompt = f"""
    You are a professional email writer helping a CS student apply for a job.
    Write a concise, personalized cold email to the hiring manager.

    Job Title: {state['job_title']}
    Company: {state['company_name']}
    Job Description: {state['job_description']}

    Hiring Manager: {state['hiring_manager_name']}
    Hiring Manager Title: {state['hiring_manager_title']}

    Qualifier Reasoning (what to emphasize and address):
    {state['qualifier_reasoning']}

    Candidate Experience:
    {candidate_context}

    Reviewer Feedback from previous draft (if any):
    {state.get('review_feedback', 'None - this is the first draft')}

    Rules:
    - Keep it under 200 words
    - Open with a specific personalized line about the company or role
    - Highlight the 2-3 strongest matches from the qualifier reasoning
    - Reference specific projects or experiences from the candidate's background that are relevant to this role
    - Use concrete details — project names, technologies, measurable outcomes — not vague claims
    - Do not use phrases like "I am passionate" or "I am a quick learner"
    - End with a clear call to action
    - Do not mention this email was AI generated
    - Sign off with this exact signature:
      Dominic Fiorelli
      linkedin.com/in/dominicfiorelli-13794a238

    Return only the email text, nothing else.
    """

    response = llm.invoke(prompt)

    return {
        "draft_email": response.content.strip(),
        "review_feedback": ""  # reset feedback after each new draft
    }