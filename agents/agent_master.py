
import yaml
from models.huggingface_model import HuggingFaceJSONModel 
from models.ollama_model import OllamaJSONModel
# from models.groq_models import GroqModel, GroqJSONModel



class Agent:
    def __init__(self, config, state, model=None, server=None, temperature=0, model_endpoint=None, stop=None, guided_json=None):
        self.config=config
        self.state = state
        self.model = model
        self.server = server
        self.temperature = temperature
        self.model_endpoint = model_endpoint
        self.stop = stop
        self.guided_json = guided_json

        if server is None:
            self.server = 'ollama'
        if model is None:
            self.model = 'llama3.2'
        
        

    def get_llm(self, json_model=True):
        if self.server == 'hf':
            return HuggingFaceJSONModel(model=self.model, temperature=self.temperature) #if json_model else get_open_ai(model=self.model, temperature=self.temperature)
        if self.server == 'ollama':
            return OllamaJSONModel(model=self.model, temperature=self.temperature) #if json_model else OllamaModel(model=self.model, temperature=self.temperature)
         

    def update_state(self, key, value):
        self.state = {**self.state, key: value}
    



class EndNodeAgent(Agent):
    def invoke(self):
        self.update_state("end_chain", "end_chain")
        return self.state