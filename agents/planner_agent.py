from termcolor import colored
import time, json, re
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
        for _ in range(3):  # Retry 3 times
            try:     
                ai_msg = llm.invoke(messages)
                response = ai_msg.content
                break  # Exit the loop if successful
            except Exception as e:
                print(f"Model is still loading....\n {e}")
                time.sleep(20)  # Wait 20 seconds before retrying
        else:
            print("Failed to load the model after multiple retries.")

        # Extract JSON portion using regex
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            print_response = json.loads(json_str)
        else:
            print("No valid JSON found!")
        # print_response = json.loads(response)

        print(colored(f"\nPlanner Agent has decided on the following next course of action👩🏿‍💻\n", 'red'))
        print(colored(f"Next Agent chosen :                {print_response['next_agent']}", 'red'))
        print(colored(f"Strategy to accomplish the task :  {print_response['overall_strategy']}", 'red'))
        print(colored(f"Reasoning provided :               {print_response['strategy_reason']}\n", 'red'))

        self.update_state("planner_response", response)
        return self.state