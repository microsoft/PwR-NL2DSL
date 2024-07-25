from calendar import c
from sys import api_version
from openai import AzureOpenAI, OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import json
import os

if os.getenv("AZURE_OPENAI_API_KEY"):
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint, api_key=azure_key, api_version=api_version
    )
else:
    client = OpenAI()

GPT_MODEL = os.getenv('MODEL_NAME')

if GPT_MODEL is None:
    raise EnvironmentError("MODEL_NAME environment variable is not set.")


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(10))
def mini_llm(utterance, model="gpt-4-turbo", temperature=0.3):

    client = AzureOpenAI()
    messages = [{"role": "system", "content": utterance}]
    completions = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return completions.choices[0].message.content


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(10))
def chat_completion_request(
    messages, tools=None, tool_choice=None, model=GPT_MODEL, response_format=None
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
