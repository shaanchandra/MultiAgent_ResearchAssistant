from termcolor import colored
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.llms import Ollama
from langchain_core.tools import tool
from langchain import hub
from langgraph.prebuilt import create_react_agent

from utils.utils import get_current_utc_datetime, check_for_content
from states import AgentGraphState
from agents.agent_master import Agent
from prompts.sqlagent_prompt import sqlagent_prompt
    





class SQLAgent(Agent):
    def invoke(self, research_question, prompt=sqlagent_prompt, feedback=None):
        db = SQLDatabase.from_uri(self.config['sqldb_dir'])
        @tool
        def db_query_tool(query: str) -> str:
            result = db.run_no_throw(query)
            if not result:
                return "Error: Query failed. Please rewrite your query and try again."
            return result
    
        print(db.run("SELECT * FROM patient_survival LIMIT 10;"))
        llm = self.get_llm()

        # llm = Ollama(
        #     model=self.model,       # e.g., "llama2"
        #     base_url=llm.model_endpoint    # e.g., "http://localhost:11434"
        # )

        sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        tools = sql_toolkit.get_tools()
        list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
        get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
        print(list_tables_tool.invoke(""))
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

        self.update_state("sqlagent_response", response)
        return self.state