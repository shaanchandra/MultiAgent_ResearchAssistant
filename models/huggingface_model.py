import requests
import json
import os
from utils.utils import load_config
from langchain_core.messages.human import HumanMessage
from huggingface_hub import InferenceClient
import requests
from langchain.schema import HumanMessage
import os
import json

class HuggingFaceJSONModel:
    def __init__(self, temperature=0, model="meta-llama/Meta-Llama-3-8B"):
        config_path = os.path.join('config.yaml')
        load_config(config_path)
        self.api_token = os.environ.get("HF_API_KEY")
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.temperature = temperature
        self.model = model

    def invoke(self, messages):
        system = messages[0]["content"]
        user = messages[1]["content"]

        prompt = f"""<|system|>
        {system}
        Your output MUST be valid JSON. Return ONLY the JSON object, no additional text.</s>
        <|user|>
        {user}</s>
        <|assistant|>
        """

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": self.temperature,
                "max_new_tokens": 1024,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                raise ValueError(f"API Error {response.status_code}: {response.text}")

            response_json = response.json()
            generated_text = response_json[0]['generated_text']
            
            # Clean response
            generated_text = generated_text.strip().replace('```json', '').replace('```', '')
            parsed = json.loads(generated_text)            
            return HumanMessage(content=json.dumps(parsed))
            
        except Exception as e:
            error_message = f"Error in invoking model! {str(e)}"
            print("ERROR", error_message)
            return HumanMessage(content=json.dumps({"error": error_message}))