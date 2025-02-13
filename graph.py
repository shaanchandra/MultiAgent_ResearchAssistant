import json
import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from agents.planner_agent import PlannerAgent
from agents.sql_agent import SQLAgent
from agents.rag_agent import RAGAgent
from agents.websearch_agent import WebSearchAgent
from agents.reviewer_agent import ReviewerAgent
from agents.agent_master import EndNodeAgent

from prompts.planner_prompt import planner_prompt, planner_guided_json
from prompts.sqlagent_prompt import sqlagent_prompt
from prompts.ragagent_prompt import ragagent_prompt
from prompts.reviewer_prompt import reviewer_prompt
# from tools.google_serper import get_google_serper
from states import AgentGraphState, get_agent_graph_state, state




def create_graph(config=None, server=None, model=None, stop=None, model_endpoint=None, temperature=0):
    graph = StateGraph(AgentGraphState)

    graph.add_node(
        "planner", 
        lambda state: PlannerAgent(
            config=config,
            state=state,
            model=model,
            server=server,
            guided_json=planner_guided_json,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
            # previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all"),
            prompt=planner_prompt
        )
    )

    graph.add_node(
        "sql_agent",
        lambda state: SQLAgent(
            config=config,
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            prompt=sqlagent_prompt,
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
        )
    )

    graph.add_node(
        "websearch_agent", 
        lambda state: WebSearchAgent(
            config=config,
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            max_results=config["max_results"],
        )
    )

    graph.add_node(
        "rag_agent", 
        lambda state: RAGAgent(
            config=config,
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            vector_db_dir=config['vectordb_dir'],
            API_key=config['HF_API_KEY'],
            prompt=ragagent_prompt
        )
    )


    graph.add_node(
        "reviewer_agent", 
        lambda state: ReviewerAgent(
            config=config,
            state=state,
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint,
            temperature=temperature
        ).invoke(
            research_question=state["research_question"],
            
            prompt=reviewer_prompt
        )
    )

    

    graph.add_node("end", lambda state: EndNodeAgent(config=config, state=state).invoke())

    # Define the edges in the agent graph
    def planner_next_agent(state: AgentGraphState):
        review_list = state["planner_response"]
        if review_list:
            review = review_list[-1]
        else:
            review = "No review"

        if review != "No review":
            if isinstance(review, HumanMessage):
                review_content = review.content
            else:
                review_content = review
            
            review_data = json.loads(review_content)
            next_agent = review_data["next_agent"]
        else:
            next_agent = "end"
        print("\nInvoking the Next agent: ", next_agent)
        return next_agent
    

    # Define the edges in the agent graph
    def pass_review(state: AgentGraphState):
        review_list = state["reviewer_response"]
        if review_list:
            review = review_list[-1]
        else:
            review = "No review"

        if review != "No review":
            if isinstance(review, HumanMessage):
                review_content = review.content
            else:
                review_content = review
            
            review_data = json.loads(review_content)
            next_agent = review_data["next_agent"]
        else:
            next_agent = "end"
        print("\nInvoking the Next agent/ ending the thread: ", next_agent)
        return next_agent
    

    # Add edges and conditional edges to the graph
    graph.set_entry_point("planner")
    graph.set_finish_point("end")

    graph.add_conditional_edges(
        "planner",
        lambda state: planner_next_agent(state=state),
    )

    graph.add_edge("sql_agent", "reviewer_agent")
    graph.add_edge("rag_agent", "reviewer_agent")
    graph.add_edge("websearch_agent", "reviewer_agent")

    graph.add_conditional_edges(
        "reviewer_agent",
        lambda state: pass_review(state=state),
    )

    return graph





def compile_workflow(graph):
    workflow = graph.compile()
    return workflow