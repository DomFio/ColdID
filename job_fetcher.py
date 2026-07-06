# job_fetcher.py
# Fetches job details from a URL using Tavily
# Extracts job title, company name, and description automatically

from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from config import LLM_MODEL

def fetch_job_from_url(url: str) -> dict:
    """
    Takes a job posting URL and returns extracted job details.
    Uses Tavily to fetch page content, then LLM to extract structured info.
    Returns a dict with job_title, company_name, job_description.
    """

    # Use Tavily to fetch the page content
    search = TavilySearch(max_results=1)
    
    try:
        results = search.invoke(url)
        
        # Handle both dict and string responses
        if isinstance(results, dict):
            content = results.get('results', [{}])[0].get('content', '')
        else:
            content = str(results)
            
        if not content:
            return {"error": "Could not fetch content from that URL. Try pasting the job description manually."}

    except Exception as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}

    # Use LLM to extract structured job info from the raw content
    llm = ChatOpenAI(model=LLM_MODEL)

    prompt = f"""
    Extract the following information from this job posting content.
    Return ONLY a JSON object with these exact keys, nothing else:
    {{
        "job_title": "the exact job title",
        "company_name": "the company name",
        "job_description": "the full job description text including responsibilities and qualifications"
    }}

    If you cannot find a field, use an empty string.

    Job Posting Content:
    {content[:3000]}
    """

    response = llm.invoke(prompt)

    import json
    try:
        # Clean response and parse JSON
        clean = response.content.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean.strip())
        return result
    except:
        return {"error": "Could not parse job details from that URL. Try pasting the job description manually."}