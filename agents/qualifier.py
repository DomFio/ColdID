# agents/qualifier.py
# Qualifier Agent - first gate in the ColdIQ pipeline
# Takes the job listing and scores how well the applicant matches
# If score is below the threshold in config.py, the pipeline stops here

from langchain_google_genai import ChatGoogleGenerativeAI
from config import LLM_MODEL, QUALIFIER_THRESHOLD
from state import ColdIQState

def qualifier_agent(state: ColdIQState) -> dict:
    """
    Reads the job listing from state.
    Queries the RAG system for relevant applicant info.
    Returns a match score and reasoning.
    """

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL)

    # Prompt tells the LLM exactly what to do and how to respond
    prompt = f"""
    You are a job application qualifier. Your job is to score how well a candidate 
    matches a job posting on a scale of 0 to 100.

    Job Title: {state['job_title']}
    Company: {state['company_name']}
    Job Description: {state['job_description']}
    Required Skills: {state['required_skills']}

    Candidate Information:
    [RAG RETRIEVAL WILL GO HERE]

    Return your response in this exact format:
    SCORE: <number>
    REASONING: <explanation of score, what matches well, what gaps exist, what to emphasize>
    """

    response = llm.invoke(prompt)

    # Parse the score and reasoning out of the response
    lines = response.content.strip().split("\n")
    score = int(lines[0].replace("SCORE:", "").strip())
    reasoning = lines[1].replace("REASONING:", "").strip()

    return {
        "qualifier_score": score,
        "qualifier_reasoning": reasoning
    }