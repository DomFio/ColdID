# main.py
# Entry point for ColdIQ pipeline
# Builds the LangGraph graph and connects all four agents
# Run this file to kick off the pipeline

from langgraph.graph import StateGraph, END
from state import ColdIQState
from agents.qualifier import qualifier_agent
from agents.finder import finder_agent
from agents.drafter import drafter_agent
from agents.reviewer import reviewer_agent
from config import QUALIFIER_THRESHOLD

# ---- CONDITIONAL EDGE FUNCTIONS ----
# These functions look at the state and decide where to go next
# They are the decision making logic of the pipeline

def should_continue_after_qualifier(state: ColdIQState) -> str:
    """
    After qualifier runs, check the score.
    If below threshold, stop the pipeline.
    If above threshold, continue to finder.
    """
    if state['qualifier_score'] < QUALIFIER_THRESHOLD:
        print(f"Score {state['qualifier_score']} is below threshold. Stopping pipeline.")
        return "stop"
    return "continue"

def should_continue_after_review(state: ColdIQState) -> str:
    """
    After reviewer runs, check if email was approved.
    If approved, move to human approval checkpoint.
    If rejected, loop back to drafter for revision.
    """
    if state['approved']:
        return "approved"
    return "revise"

def extract_skills(job_description: str) -> list[str]:
    """
    Uses the LLM to automatically extract required skills from a job description.
    Saves the user from having to manually identify and list skills.
    """
    from langchain_openai import ChatOpenAI
    from config import LLM_MODEL

    llm = ChatOpenAI(model=LLM_MODEL)

    prompt = f"""
    Extract the key required technical skills and technologies from this job description.
    Return ONLY a Python list of strings, nothing else. No explanation, no preamble.
    Focus on specific technologies, languages, frameworks, and tools.
    Limit to the 8 most important ones.

    Example output format:
    ["Python", "LangChain", "SQL", "HuggingFace", "RAG", "Git"]

    Job Description:
    {job_description}
    """

    response = llm.invoke(prompt)

    # Parse the list from the response
    import ast
    try:
        skills = ast.literal_eval(response.content.strip())
        return skills
    except:
        # Fallback if parsing fails
        return ["Python", "SQL"]

# ---- BUILD THE GRAPH ----

def build_graph():
    # Initialize the graph with our state schema
    graph = StateGraph(ColdIQState)

    # Add all four agents as nodes
    graph.add_node("qualifier", qualifier_agent)
    graph.add_node("finder", finder_agent)
    graph.add_node("drafter", drafter_agent)
    graph.add_node("reviewer", reviewer_agent)

    # Set the entry point - qualifier always runs first
    graph.set_entry_point("qualifier")

    # Conditional edge after qualifier
    # Either stops or continues to finder based on score
    graph.add_conditional_edges(
        "qualifier",
        should_continue_after_qualifier,
        {
            "stop": END,
            "continue": "finder"
        }
    )

    # Finder always goes to drafter
    graph.add_edge("finder", "drafter")

    # Conditional edge after reviewer
    # Either loops back to drafter or ends pipeline
    graph.add_conditional_edges(
        "reviewer",
        should_continue_after_review,
        {
            "approved": END,
            "revise": "drafter"
        }
    )

    # Drafter always goes to reviewer
    graph.add_edge("drafter", "reviewer")

    # Compile and return the graph
    return graph.compile()


# ---- RUN THE PIPELINE ----

if __name__ == "__main__":
    app = build_graph()

    # ---- CLI INPUT FLOW ----
    print("\n" + "="*60)
    print("Welcome to ColdIQ — AI-Powered Job Application Pipeline")
    print("="*60 + "\n")

    # Collect job info
    job_title = input("Job Title: ").strip()
    company_name = input("Company Name: ").strip()

    # Collect job description from file or manual input
    print("\nHow would you like to provide the job description?")
    print("1 - Read from job.txt file")
    print("2 - Paste manually")
    jd_choice = input("\nChoice (1 or 2): ").strip()

    if jd_choice == "1":
        try:
            with open("job.txt", "r", encoding="utf-8") as f:
                job_description = f.read().strip()
            print("✓ Job description loaded from job.txt")
        except FileNotFoundError:
            print("job.txt not found. Switching to manual input.")
            jd_choice = "2"

    if jd_choice == "2":
        print("\nPaste the Job Description (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "":
                if lines:
                    break
            else:
                lines.append(line)
        job_description = "\n".join(lines)

    # Auto extract skills
    print("\nExtracting required skills from job description...")
    required_skills = extract_skills(job_description)
    print(f"✓ Skills identified: {required_skills}")

    # Ask about hiring manager
    print("\nDo you know the hiring manager? (y/n): ", end="")
    knows_hiring_manager = input().strip().lower()

    hiring_manager_name = ""
    hiring_manager_title = ""
    hiring_manager_linkedin = ""

    if knows_hiring_manager == "y":
        hiring_manager_name = input("Hiring Manager Name: ").strip()
        hiring_manager_title = input("Hiring Manager Title: ").strip()
        hiring_manager_linkedin = input("Hiring Manager LinkedIn (or leave blank): ").strip()

    print("\nRunning ColdIQ pipeline...\n")

    # Build the input state
    pipeline_input = {
        "job_title": job_title,
        "company_name": company_name,
        "job_description": job_description,
        "required_skills": required_skills,
        "qualifier_score": 0,
        "qualifier_reasoning": "",
        "hiring_manager_name": hiring_manager_name,
        "hiring_manager_title": hiring_manager_title,
        "hiring_manager_linkedin": hiring_manager_linkedin,
        "hiring_manager_email": "",
        "draft_email": "",
        "review_feedback": "",
        "approved": False,
        "review_loops": 0,
        "date_applied": "",
        "outcome": ""
    }

    result = app.invoke(pipeline_input)

    print("\n" + "="*60)
    print("COLDIQ PIPELINE RESULTS")
    print("="*60)
    print(f"\nJob: {result['job_title']} at {result['company_name']}")
    print(f"Qualifier Score: {result['qualifier_score']}/100")
    print(f"\nQualifier Reasoning:\n{result['qualifier_reasoning']}")
    print(f"\nHiring Manager: {result['hiring_manager_name']} ({result['hiring_manager_title']})")
    print(f"LinkedIn: {result['hiring_manager_linkedin']}")
    print(f"\n{'='*60}")
    print("DRAFT EMAIL:")
    print("="*60)
    print(result['draft_email'])
    print(f"\n{'='*60}")
    print(f"Approved: {result['approved']}")
    print(f"Review Loops: {result['review_loops']}")
    print(f"Final Feedback: {result['review_feedback']}")
    print("="*60)