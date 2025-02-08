from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    research_question: str
    system_response: str
    planner_response: Annotated[list, add_messages]
    sqlagent_response: Annotated[list, add_messages]
    ragagent_response: Annotated[list, add_messages]
    websearch_agent_response: Annotated[list, add_messages]
    reviewer_response: Annotated[list, add_messages]
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
    
    elif state_key == "websearch_all":
        return state["websearch_agent_response"]
    elif state_key == "websearch_latest":
        return state["websearch_agent_response"][-1] if state["websearch_agent_response"] else state["websearch_agent_response"]
    
    elif state_key == "reviewer_all":
        return state["reviewer_response"]
    elif state_key == "reviewer_latest":        
        return state["reviewer_response"][-1] if state["reviewer_response"] else state["reviewer_response"]
        
    else:
        return None
    
state = {
    "research_question":"",
    "system_response": "",
    "planner_response": [],
    "sqlagent_response": [],
    "ragagent_response": [],
    "websearch_agent_response": [],
    "reviewer_response": [],
    "end_chain": []
}