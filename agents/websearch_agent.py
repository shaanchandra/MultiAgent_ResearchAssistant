import json, pprint
from termcolor import colored
from prompts.planner_prompt import sql_prompt
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain import hub

from langgraph.prebuilt import create_react_agent

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent



class WebSearchAgent(Agent):
    def invoke(self, research_question, prompt=None, max_results=3, feedback=None):
        web_search_tool = TavilySearchResults(max_results=max_results,
                                            include_answer=True,
                                            include_raw_content=True,
                                            include_images=True,
                                            # search_depth="advanced",
                                            # include_domains = []
                                            # exclude_domains = []
                                            )
        
        response = web_search_tool.invoke({"args": {'query': research_question}, "type": "tool_call", "name": "AI RA"})
        response_artefact = {k: str(v)[:500] for k, v in response.artifact.items()} # keys are : query, follow_up_questions, answer, images, results, response_time

        print(colored("WebSearch Agent 👩🏿‍💻: I am ready to help you with your web-based queries.", "green"))
        print(colored(f"You asked : {research_question}", "green"))
        print(colored(f"The answer that I could find is : {response_artefact['answer']}", "green"))
        print(colored(f"The URLs I used :", "green"))
        for result in response_artefact['results']:
            print(colored(f"Title : {result['title']} ,   URL : {result['url']}", "green"))
            print("---")

        self.update_state("websearch_agent_response", response_artefact)
        return self.state


