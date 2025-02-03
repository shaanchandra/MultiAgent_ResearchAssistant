from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    research_question: str
    planner_response: Annotated[list, add_messages]
    sqlagent_response: Annotated[list, add_messages]
    ragagent_response: Annotated[list, add_messages]
    reviewer_response: Annotated[list, add_messages]
    # router_response: Annotated[list, add_messages]
    # serper_response: Annotated[list, add_messages]
    # scraper_response: Annotated[list, add_messages]
    final_reports: Annotated[list, add_messages]
    end_chain: Annotated[list, add_messages]

# Define the nodes in the agent graph
def get_agent_graph_state(state:AgentGraphState, state_key:str):
    if state_key == "planner_all":
        return state["planner_response"]
    elif state_key == "planner_latest":
        return state["planner_response"][-1] if state["planner_response"] else state["planner_response"]
    
    elif state_key == "sql_all":
        return state["sqlagent_response"]
    elif state_key == "sql_latest":
        return state["sqlagent_response"][-1] if state["sqlagent_response"] else state["sqlagent_response"]
    
    elif state_key == "rag_all":
        return state["ragagent_response"]
    elif state_key == "rag_latest":
        return state["ragagent_response"][-1] if state["ragagent_response"] else state["ragagent_response"]
        
    # elif state_key == "serper_all":
    #     return state["serper_response"]
    # elif state_key == "serper_latest":
    #     if state["serper_response"]:
    #         return state["serper_response"][-1]
    #     else:
    #         return state["serper_response"]
    
    # elif state_key == "scraper_all":
    #     return state["scraper_response"]
    # elif state_key == "scraper_latest":
    #     if state["scraper_response"]:
    #         return state["scraper_response"][-1]
    #     else:
    #         return state["scraper_response"]
    
    elif state_key == "reviewer_all":
        return state["reviewer_response"]
    elif state_key == "reviewer_latest":
        if state["reviewer_response"]:
            return state["reviewer_response"][-1]
        else:
            return state["reviewer_response"]
        
    else:
        return None
    
state = {
    "research_question":"",
    "planner_response": [],
    "sqlagent_response": [],
    "ragagent_response": [],
    "reviewer_response": [],
    # "router_response": [],
    # "serper_response": [],
    # "scraper_response": [],
    "final_reports": [],
    "end_chain": []
}