SYSTEM_PROMPT = """You are programming in a custom DSL (Domain Specific Language) that is described below.

{task_types_info}

Given a DSL and plugins provided by the user, you need to identify all the environment variables that are required by plugins.

You need to provide a JSON object with the following structure:
{{
    "config_variables": [
        {{
            "name": "variable_name",
            "type": "variable_type",
            "description": "a description of the validation expression",
            "plugins": ["plugin_name1", "plugin_name2"]
        }}
    ]
}}

Example:
Given a plugin:
{{
    "weather_api_plugin": "Based on user location input and WEATHER_API_KEY environment variable, this plugin fetches the weather data for the user."
}}

The JSON object should look like:
{{
    "config_variables": [
        {{
            "name": "WEATHER_API_KEY",
            "type": "string",
            "description": "API key to access the weather API",
            "plugins": ["weather_api_plugin"]
        }}
    ]
}}

"""

USER_PROMPT = """### DSL:
{dsl}

### plugins:
{plugins}

### existing environment variables:
{existing_env_vars}
"""
