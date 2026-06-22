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

    # Test input - we'll replace this with real input later
test_input = {
    "job_title": "Software Engineer",
    "company_name": "Test Company",
    "job_description": "Test job description.",
    "required_skills": ["Python", "SQL"],   
    "qualifier_score": 0,
    "qualifier_reasoning": "",
    "hiring_manager_name": "",
    "hiring_manager_title": "",
    "hiring_manager_linkedin": "",
    "hiring_manager_email": "",
    "draft_email": "",
    "review_feedback": "",
    "approved": False,
    "review_loops": 0,
    "date_applied": "",
    "outcome": ""
}

result = app.invoke(test_input)
# print(result)


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