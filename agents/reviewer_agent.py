from termcolor import colored
import json, re
# from models.groq_models import GroqModel, GroqJSONModel

from prompts.reviewer_prompt import reviewer_prompt
from states import AgentGraphState, get_agent_graph_state, state
from langchain_core.messages import HumanMessage

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent

 
 

class ReviewerAgent(Agent):
    def invoke(self, research_question, prompt=reviewer_prompt, feedback=None):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        latest_state = get_agent_graph_state(state=self.state, state_key="planner_latest")
        if isinstance(latest_state, HumanMessage):
            review_content = latest_state.content
        else:
            review_content = latest_state
        
        review_data = json.loads(review_content)
        last_agent_used = review_data["next_agent"]

        if last_agent_used=='sql_agent':
            agent_response = get_agent_graph_state(state=self.state, state_key="sql_latest")
        elif last_agent_used=='rag_agent':
            agent_response = get_agent_graph_state(state=self.state, state_key="rag_latest")
        elif last_agent_used=='websearch_agent':
            agent_response = get_agent_graph_state(state=self.state, state_key="websearch_latest")
        else:
            print("[!] Could not identify the Agent response from planner state!")
        
        reviewer_prompt = prompt.format(planner_response=last_agent_used + ",   " + review_data['overall_strategy'], agent_response=agent_response)


        messages = [
            {"role": "system", "content": reviewer_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content
        # Extract JSON portion using regex
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            print_response = json.loads(json_str)
        else:
            print("No valid JSON found!")
        print(print_response)


        print(colored(f"\nReviewer Agent provides its evluation 👩🏿‍💻", 'cyan'))
        print(colored(f"Next Agent chosen :             {print_response['next_agent']}", 'cyan'))
        print(colored(f"Eval of planner's plan :        {print_response['planner_review']}", 'cyan'))
        print(colored(f"Eval of agent's response :      {print_response['agent_review']}", 'cyan'))
        print(colored(f"Any additional instructions :   {print_response['additional_info']}", 'cyan'))

        self.update_state("reviewer_response", response)
        return self.state