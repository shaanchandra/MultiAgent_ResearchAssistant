from termcolor import colored
# from models.groq_models import GroqModel, GroqJSONModel

from prompts.planner_prompt import planner_prompt, planner_guided_json

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent

 


class PlannerAgent(Agent):
    def invoke(self, research_question, prompt=planner_prompt, feedback=None):
        feedback_value = feedback() if callable(feedback) else feedback
        feedback_value = check_for_content(feedback_value)

        planner_prompt = prompt.format(feedback=feedback_value)

        messages = [
            {"role": "system", "content": planner_prompt},
            {"role": "user", "content": f"research question: {research_question}"}
        ]

        llm = self.get_llm()
        ai_msg = llm.invoke(messages)
        response = ai_msg.content

        print(colored(f"Planner Agent has decided on the following next course of action👩🏿‍💻", 'red'))
        print(colored(f"Next Agent chosen :  {response['next_agent']}", 'red'))
        print(colored(f"Strategy to accomplish the task :  {response['overall_strategy']}", 'red'))
        print(colored(f"Reasoning provided :  {response['strategy_reason']}", 'red'))

        self.update_state("planner_response", response)
        return self.state