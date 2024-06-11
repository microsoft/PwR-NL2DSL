SYSTEM_PROMPT = """ 
plugin: {plugins}

From the above plugins, extract the possible return codes of the plugin with id {plugin_id}. Respond with a list of the return codes ONLY FOR {plugin_id} as strings and nothing else. Any wrong or excess return codes and you will lose 10 points.
Your response will be directly parsed using the python function json.loads()
Example Response: ["200", "404"]
"""
