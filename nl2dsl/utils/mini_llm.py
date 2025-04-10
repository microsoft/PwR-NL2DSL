from openai import AzureOpenAI, OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from azure.identity import AzureCliCredential, get_bearer_token_provider
import json
import os

if os.getenv("OPENAI_API_TYPE") == "custom":
    api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
    if not api_endpoint:
        raise EnvironmentError("OPENAI_API_ENDPOINT environment variable is not set.")

    api_version = os.getenv("OPENAI_API_VERSION")
    if api_key := os.getenv("OPENAI_API_KEY", None):
        client = AzureOpenAI(
            azure_endpoint=api_endpoint,
            api_key=api_key,
            api_version=api_version,
        )
    else:
        scope = os.getenv("AZURE_CREDENTIAL_SCOPE")
        if not scope:
            raise EnvironmentError("AZURE_CREDENTIAL_SCOPE environment variable is not set.")
        credential = get_bearer_token_provider(AzureCliCredential(), scope)
        client = AzureOpenAI(
            azure_endpoint=api_endpoint,
            azure_ad_token_provider=credential,
            api_version=api_version,
        )
else:
    client = OpenAI()

SLOW_MODEL = os.getenv("SLOW_MODEL")

if SLOW_MODEL is None:
    raise EnvironmentError("SLOW_MODEL environment variable is not set.")


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(10))
def chat_completion_request(
    messages, tools=None, tool_choice=None, model=SLOW_MODEL, response_format=None
):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        response_format=response_format,
    )
    return response


def call_llm_for_json(system_prompt, user_prompt) -> dict | list:

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {"role": "user", "content": user_prompt},
    ]

    chat_response = chat_completion_request(
        messages, response_format={"type": "json_object"}
    )
    # cprint(chat_response, "yellow")
    # cprint(chat_response.choices[0].message.content, "light_yellow")
    return json.loads(chat_response.choices[0].message.content)
