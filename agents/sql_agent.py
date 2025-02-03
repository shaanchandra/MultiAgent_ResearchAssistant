from termcolor import colored
from prompts.planner_prompt import sql_prompt
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain import hub
from langgraph.prebuilt import create_react_agent

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent
from prompts.sqlagent_prompt import sqlagent_prompt
 

class SQLAgent(Agent):
    def invoke(self, research_question, prompt=sqlagent_prompt, feedback=None):
        db = SQLDatabase.from_uri(self.config['sqldb_dir'])
        llm = self.get_llm()

        sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        assert len(prompt_template.messages) == 1
        system_message = prompt_template.format(dialect="SQLite", top_k=1)
        agent_executor = create_react_agent(llm, sql_toolkit.get_tools(), prompt=system_message)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"research question: {research_question}"}]

        # events = agent_executor.stream(
        #     {"messages": messages})
        
        print(colored("SQL Agent 👩🏿‍💻: I am ready to help you with your SQL queries.", "yellow"))
        for chunk in agent_executor.stream({"messages": messages}):
            # Agent Action
            if "actions" in chunk:
                for action in chunk["actions"]:
                    print(colored(f"Calling Tool: `{action.tool}` with input `{action.tool_input}`", 'yellow'))
            # Observation
            elif "steps" in chunk:
                for step in chunk["steps"]:
                    print(colored(f"Tool Result: `{step.observation}`", "yellow"))
            # Final result
            elif "output" in chunk:
                print(colored(f'Final Output: {chunk["output"]}', 'yellow'))
                response = chunk["output"]
            else:
                raise ValueError()
            print("---")


        # response = events[-1]["messages"][-1].content

        # feedback_value = feedback() if callable(feedback) else feedback
        # feedback_value = check_for_content(feedback_value)
        # sql_prompt = prompt.format(feedback=feedback_value)        

        # ai_msg = llm.invoke(messages)
        # response = ai_msg.content

        self.update_state("sqlagent_response", response)
        return self.state