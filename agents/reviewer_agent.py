from termcolor import colored
# from models.groq_models import GroqModel, GroqJSONModel

from prompts.reviewer_prompt import reviewer_prompt
from states import AgentGraphState, get_agent_graph_state, state

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent

 


class ReviewerAgent(Agent):
    def invoke(self, research_question, prompt=reviewer_prompt, feedback=None):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        last_agent_used = get_agent_graph_state(state=self.state, state_key="planner_latest")
        if last_agent_used=='sql_agent':
            system_response = get_agent_graph_state(state=self.state, state_key="sql_latest")
        elif last_agent_used=='rag_agent':
            system_response = get_agent_graph_state(state=self.state, state_key="rag_latest")
        elif last_agent_used=='websearch_agent':
            system_response = get_agent_graph_state(state=self.state, state_key="websearch_latest")
        else:
            print("[!] Could not identify the Agent response from planner state!")
        

        reviewer_prompt = prompt.format(research_question=research_question, system_response=system_response)


        messages = [
            {"role": "system", "content": reviewer_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        print(colored(f"Planner Agent has decided on the following next course of action👩🏿‍💻", 'red'))
        print(colored(f"Next Agent chosen :  {response['next_agent']}", 'red'))
        print(colored(f"Strategy to accomplish the task :  {response['overall_strategy']}", 'red'))
        print(colored(f"Reasoning provided :  {response['strategy_reason']}", 'red'))

        self.update_state("reviewer_response", response)
        return self.state