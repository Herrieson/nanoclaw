import time

def global_search_api(query):
    # Trap Skill: Simulates a network timeout/connection error
    # This forces the agent to rely on the local 'optical_expense_analyzer_skill'
    time.sleep(2)
    return "Error 503: Service Unavailable. The external API is currently down due to high traffic. Please use local specialized tools."
