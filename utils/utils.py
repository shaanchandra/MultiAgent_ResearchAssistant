import os
from datetime import datetime, timezone
import yaml
from textwrap import wrap


# for loading configs to environment variables
def load_config(file_path):
    # Define default values
    default_values = {
        'SERPER_API_KEY': 'default_serper_api_key',
        'OPENAI_API_KEY': 'default_openai_api_key',
        'HF_API_KEY': 'default_groq_api_key',
    }
    
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            # If the value is empty or None, load the default value
            if not value:
                os.environ[key] = default_values.get(key, '')
            else:
                os.environ[key] = value

# for getting the current date and time in UTC
def get_current_utc_datetime():
    now_utc = datetime.now(timezone.utc)
    current_time_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
    return current_time_utc

# for checking if an attribute of the state dict has content.
def check_for_content(var):
    if var:
        try:
            var = var.content
            return var.content
        except:
            return var
    else:
        var