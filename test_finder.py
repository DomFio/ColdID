# test_finder.py
from agents.finder import finder_agent

test_state = {
    "job_title": "Remote JR AI Engineer",
    "company_name": "Insight Global"
}

result = finder_agent(test_state)
print(result)