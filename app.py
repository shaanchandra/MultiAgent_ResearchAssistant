
from graph import create_graph, compile_workflow
import yaml
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
# server = 'ollama'
# model = 'llama3:instruct'
# model_endpoint = None


# Run a model using HuggingFace
server = 'hf'
model = 'meta-llama/Meta-Llama-3-8B'
model_endpoint = None


# server = 'vllm'
# model = 'meta-llama/Meta-Llama-3-70B-Instruct' # full HF path
# model_endpoint = 'https://kcpqoqtjz0ufjw-8000.proxy.runpod.net/' 
# #model_endpoint = runpod_endpoint + 'v1/chat/completions'
# stop = "<|end_of_text|>"

iterations = 40


print("-"*100 + "Welcome to the AI Research Assistant" + "-"*100)
print ("\n>> Creating graph and compiling workflow...")
graph = create_graph(config=config, server=server, model=model, model_endpoint=model_endpoint)
workflow = compile_workflow(graph)
print (">> Graph and workflow created.")





if __name__ == "__main__":
    verbose = False

    while True:
        query = input("Please enter your research question: ")
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



    