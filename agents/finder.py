# agents/finder.py
# Finder Agent - second agent in the ColdIQ pipeline
# Takes company name and job title from state
# Uses Tavily to search the web for the hiring manager
# Outputs hiring manager name, title, and LinkedIn into state

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from config import LLM_MODEL
from state import ColdIQState

def finder_agent(state: ColdIQState) -> dict:
    """
    Checks if hiring manager info already exists in state.
    If not, uses Tavily to search for the hiring manager.
    Skips search if info is already provided.
    """

    # If hiring manager info is already in state, skip the search
    if state.get('hiring_manager_name') and state['hiring_manager_name'] != "not found":
        print(f"DEBUG - Hiring manager already known: {state['hiring_manager_name']}, skipping search")
        return {
            "hiring_manager_name": state['hiring_manager_name'],
            "hiring_manager_title": state['hiring_manager_title'],
            "hiring_manager_linkedin": state['hiring_manager_linkedin']
        }

    # Otherwise run the search
    print("DEBUG - No hiring manager found in state, searching...")

    # Initialize the LLM and Tavily search tool
    llm = ChatOpenAI(model=LLM_MODEL)
    search = TavilySearch(max_results=5)

    # Build a search query from the job info in state
    query = f"{state['company_name']} engineering manager OR recruiter OR talent site:linkedin.com/in"
    print(f"DEBUG - Query: {query}")

    # Run the search
    search_results = search.invoke(query)
    print(f"DEBUG - Search Results: {search_results}")

    # Pass results to LLM to extract the relevant person
    prompt = f"""
    You are helping find the hiring manager for a job application.
    
    IMPORTANT: Only extract a person if their LinkedIn profile clearly and explicitly 
    shows they currently work at the EXACT company "{state['company_name']}". 
    Many companies share similar or generic names - do not match based on partial 
    or similar company names. If you are not highly confident, return "not found" 
    for all fields.

    Job Title: {state['job_title']}
    Company: {state['company_name']}

    Search Results:
    {search_results}

    From these results extract the most likely hiring manager who is CONFIRMED 
    to work at {state['company_name']} specifically.
    Return your response in this exact format:
    NAME: <full name>
    TITLE: <job title>
    LINKEDIN: <linkedin url or "not found">
    """

    response = llm.invoke(prompt)
    print(f"DEBUG - LLM Response: {response.content}")

    # Parse the response
    lines = response.content.strip().split("\n")
    name = lines[0].replace("NAME:", "").strip()
    title = lines[1].replace("TITLE:", "").strip()
    linkedin = lines[2].replace("LINKEDIN:", "").strip()

    return {
        "hiring_manager_name": name,
        "hiring_manager_title": title,
        "hiring_manager_linkedin": linkedin
    }