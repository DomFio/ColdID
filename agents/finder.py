# agents/finder.py
# Finder Agent - second agent in the ColdIQ pipeline
# Takes company name and job title from state
# Uses Tavily to search the web for the hiring manager
# Outputs hiring manager name, title, and LinkedIn into state

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from config import LLM_MODEL
from state import ColdIQState

def finder_agent(state: ColdIQState) -> dict:
    """
    Uses Tavily to search for the hiring manager at the target company.
    Extracts name, title, and LinkedIn profile from search results.
    """

    # Initialize the LLM and Tavily search tool
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL)
    search = TavilySearchResults(max_results=5)

    # Build a search query from the job info in state
    query = f"hiring manager {state['job_title']} at {state['company_name']} LinkedIn"

    # Run the search
    search_results = search.invoke(query)

    # Pass results to LLM to extract the relevant person
    prompt = f"""
    You are helping find the hiring manager for a job application.

    Job Title: {state['job_title']}
    Company: {state['company_name']}

    Search Results:
    {search_results}

    From these results extract the most likely hiring manager.
    Return your response in this exact format:
    NAME: <full name>
    TITLE: <job title>
    LINKEDIN: <linkedin url or "not found">
    """

    response = llm.invoke(prompt)

    # Parse the response
    lines = response.content.strip().split("\n")