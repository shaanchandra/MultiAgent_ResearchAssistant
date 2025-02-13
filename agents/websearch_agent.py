import json, pprint
from termcolor import colored
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.utilities.tavily_search import TavilySearchAPIWrapper

from langchain import hub

from langgraph.prebuilt import create_react_agent

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent

# import getpass
# import os
# os.environ["TAVILY_API_KEY"] = getpass.getpass()


class WebSearchAgent(Agent):
    def invoke(self, research_question, prompt=None, max_results=3, feedback=None):

        tavilySearchAPIWrapper = TavilySearchAPIWrapper(tavily_api_key=self.config['TAVILY_API_KEY'])
        web_search_tool = TavilySearchResults(max_results=max_results,
                                            include_answer=True,
                                            include_raw_content=True,
                                            include_images=True,
                                            api_wrapper=tavilySearchAPIWrapper
                                            # search_depth="advanced",
                                            # include_domains = []
                                            # exclude_domains = []
                                            )
        
        response = web_search_tool.invoke({"args": {'query': research_question}, "type": "tool_call", "name": "AI RA", "id":"search"})
        urls = {k: v for k, v in response.artifact.items() if k=='results'}
        response_artefact = {k: str(v)[:1000] for k, v in response.artifact.items()} # keys are : query, follow_up_questions, answer, images, results, response_time
        # print(response_artefact)
        print(colored("WebSearch Agent 👩🏿‍💻: I am ready to help you with your web-based queries.", "green"))
        print(colored(f"\nYou asked : {research_question}", "green"))
        print(colored(f"\nThe answer that I could find is :\n {response_artefact['answer']}", "green"))
        print(colored(f"\nThe URLs I used :\n", "green"))
        # print(response_artefact['results'])
        # for result in response_artefact['results']:
        #     print(result)
        #     print(type(result))
        #     result = json.loads(result)
        #     print(colored(f"Title : {result['title']} ,   URL : {result['url']}", "green"))
        #     print("---")
        urls = urls['results']
        for url in urls:
            print(colored(f"Title : {url['title']} ,   URL : {url['url']}", "green"))

        self.update_state("websearch_agent_response", response)
        return self.state


