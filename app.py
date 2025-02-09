
from graph import create_graph, compile_workflow
import yaml
from termcolor import colored
from sqlalchemy import create_engine

with open("./config.yaml") as cfg:
    config = yaml.load(cfg, Loader=yaml.FullLoader)


# file_dir_list = os.listdir(config['csvfiles_dir'])

config['sqldb_dir'] = f"sqlite:///{config['sqldb_dir']}"
# config['engine'] = create_engine(db_dir)


#########################################
#####     Server & Model Options
#########################################

# Run a model using Ollama
server = 'ollama'
model = 'llama3.2'
model_endpoint = None



# # Run a model using HuggingFace
# server = 'hf'
# # model = 'meta-llama/Meta-Llama-3-8B-quantized'
# model = 'hugging-quants/Llama-3.2-1B-Instruct-Q8_0-GGUF'
# # model = 'nsloth/DeepSeek-R1-Distill-Llama-8B-GGUF/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf'
# model_endpoint = None   

iterations = 40


print("\n", "-"*100 + "\nWelcome to the AI Research Assistant\n" + "-"*100)
print(colored("\n>> Creating graph and compiling workflow...", 'green'))
graph = create_graph(config=config, server=server, model=model, model_endpoint=model_endpoint)
workflow = compile_workflow(graph)
print (colored(">> Graph and workflow created. You are all set to use the Agentic AI Research Assistant !! \n", 'green'))
print(colored(f"\nThere are three kinds of agents available currently to assist you: ", 'green'))
print(colored(f"1. SQL Agent : to assist you with structured QnA to explore your datasets in the ./data folder", 'green'))
print(colored(f"1. RAG Agent : to assist you with unstructured QnA to explore your PDFs/Papers/Articles on device", 'green'))
print(colored(f"1. WebSearch Agent : to assist you with looking up latest info from web in case it is not available on device\n\n", 'green'))

print(colored(f"-"*100, 'green'))
print(colored(f">> Note that there is an Orchestrator/Planner agent also present that can assist with more complex workflows involving multiple agents in different steps", 'green'))





if __name__ == "__main__":
    verbose = False

    while True:
        query = input("\nPlease enter your research question: ")
        if query.lower() == "exit":
            break

        dict_inputs = {"research_question": query}
        # thread = {"configurable": {"thread_id": "4"}}
        limit = {"recursion_limit": iterations}

        for event in workflow.stream(dict_inputs, limit):
            if verbose:
                print("\nState Dictionary:", event)
            else:
                print("\n")



    