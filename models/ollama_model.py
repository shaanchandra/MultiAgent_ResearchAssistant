import requests
import json
import ast
from langchain_core.messages.human import HumanMessage

# import logging, http.client
# http.client.HTTPConnection.debuglevel = 1
# logging.basicConfig(level=logging.DEBUG)

class OllamaJSONModel:
    def __init__(self, temperature=0, model="llama3.2"):
        self.headers = {"Content-Type": "application/json"}
        self.model_endpoint = "http://127.0.0.1:11434/api/generate"
        self.temperature = temperature
        self.model = model
    


    def invoke(self, prompt):
        
        payload = {
            "model": self.model,
            "prompt": str(prompt),
            "stream": False }

        try:
            # Make the API request
            response = requests.post(self.model_endpoint, headers=self.headers, json=payload)
            # response.raise_for_status()  # Raise an error for bad status codes

            # Parse the response
            response_json = response.json()
            if "response" not in response_json:
                raise ValueError("Invalid response format from Ollama API")

            # Return the response as a HumanMessage
            return HumanMessage(content=response_json["response"])

        except requests.exceptions.RequestException as e:
            # Handle connection errors
            error_message = f"Error in invoking model: {str(e)}"
            print("ERROR:", error_message)
            return HumanMessage(content=error_message)  # Return error as a string

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            # Handle invalid response format
            error_message = f"Error processing model response: {str(e)}"
            print("ERROR:", error_message)
            return HumanMessage(content=error_message)  # Return error as a string

    # def invoke(self, messages):

    #     system = messages[0]["content"]
    #     user = messages[1]["content"]

    #     payload = {
    #             "model": self.model,
    #             "prompt": user,
    #             "format": "json",
    #             "system": system,
    #             "stream": False,
    #             "temperature": 0,
    #         }
        
    #     try:
    #         request_response = requests.post(
    #             self.model_endpoint, 
    #             headers=self.headers, 
    #             data=json.dumps(payload)
    #             )
            
    #         print("REQUEST RESPONSE", request_response)
    #         request_response_json = request_response.json()
    #         # print("REQUEST RESPONSE JSON", request_response_json)
    #         response = json.loads(request_response_json['response'])
    #         response = json.dumps(response)

    #         response_formatted = HumanMessage(content=response)

    #         return response_formatted
    #     except requests.RequestException as e:
    #         response = {"error": f"Error in invoking model! {str(e)}"}
    #         response_formatted = HumanMessage(content=response)
    #         return response_formatted