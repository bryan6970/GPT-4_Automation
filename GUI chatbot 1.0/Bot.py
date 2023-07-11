import json
import os
import logging
import sys

import openai
from tkinter import messagebox

import requests
from bs4 import BeautifulSoup

# Configure logging level
logging.basicConfig(filename="logs.log", level=logging.DEBUG)

try:
    openai.api_key = os.environ.get("OPEN_AI_API_TOKEN")
except Exception as e:
    logging.error(f"Error setting OpenAI API key: {e}")
    messagebox.showerror("Error", "Failed to set OpenAI API key. Ensure that the OpenAI API key is under "
                                  "OPEN_AI_API_TOKEN in your system environment variables, "
                                  "and then restart your computer")
    sys.exit()

ERROR = False


def run_python_code(code):
    global ERROR
    ERROR = False
    try:
        exec(code)
    except Exception as e:
        ERROR = e


def extract_text_from_website(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using Beautiful Soup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all the text elements in the HTML
            text_elements = soup.find_all(text=True)

            # Filter out script and style tags
            filtered_text = [text for text in text_elements if text.parent.name not in ['script', 'style']]

            # Join the filtered text elements into a single string
            extracted_text = " ".join(filtered_text)
            logging.debug(extracted_text)
            return extracted_text

        else:
            logging.debug(f"Error: Failed to retrieve content from {url}")
            return f"Error: Failed to retrieve content from {url}"
    except Exception as e:
        logging.debug(e)
        return e


functions = [{
    "name": "run_python_code",
    "description": "runs python code with exec function",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Uses exec() to run python code",
            },
        },
        "required": ["code"],
    },
    "return_type": {"type": "null"},
},
    {
        "name": "extract_text_from_website",
        "description": "Get text content from site",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Site's full URL (with https)",
                },
            },
            "required": ["url"],
        },
        "return_type": {"type": "str"}
    }]

available_functions = {
    "run_python_code": run_python_code,
    "extract_text_from_website": extract_text_from_website,
}


def run_convo_with_function_calls(chat_history, model, max_tokens, temperature):
    try:

        model_engine = model

        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=chat_history,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
            functions=functions,
            function_call="auto"
        )

        response_message = response["choices"][0]["message"]

        # Step 2: check if GPT wanted to call a function
        if response_message.get("function_call"):
            try:
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors

                function_name = response_message["function_call"]["name"]
                function_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])

                if function_name == "run_python_code":
                    function_response = function_to_call(code=function_args.get("code"))
                elif function_name == "extract_text_from_website":
                    function_response = function_to_call(url=function_args.get("url"))

                # Step 4: send the info on the function call and function response to GPT
                # messages.append(response_message)  # extend conversation with assistant's reply

            except Exception as e:
                logging.error(f"Error with OpenAI API key: {e}")
                # messagebox.showerror("Error", e)
                return e

            if ERROR:
                logging.debug(
                    f"""Something went wrong, the code provided was {response_message.get('function_call').get('arguments')}
            The error was {ERROR}""")
                return f"""Something went wrong, the code provided was {response_message.get('function_call').get('arguments')}
            The error was {ERROR}"""
            else:
                logging.debug(
                    f"Success! The code provided was  {response_message.get('function_call').get('arguments')}")
                return f"Success! The code provided was  {response_message.get('function_call').get('arguments')}"

        else:
            logging.debug(response_message)
            return response_message.get("content")


    except Exception as e:
        logging.error(f"Error with OpenAI API key: {e}")
        # messagebox.showerror("Error", e)
        return e


def run_convo_with_function_calls_and_explanation(chat_history, model, max_tokens, temperature):
    try:

        model_engine = model

        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=chat_history,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
            functions=functions,
            function_call="auto"
        )

        response_message = response["choices"][0]["message"]

        print(response)

        print(response_message)

        # Step 2: check if GPT wanted to call a function
        if response_message.get("function_call"):
            try:
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors
                # only one function in this example, but you can have multiple

                function_name = response_message["function_call"]["name"]
                function_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])

                if function_name == "run_python_code":
                    function_response = function_to_call(code=function_args.get("code"))
                elif function_name == "extract_text_from_website":
                    function_response = function_to_call(url=function_args.get("url"))
                else:
                    return "(Developer) No function name has been declared, unable to pass args"


                if ERROR:
                    logging.debug(
                        f"""Something went wrong, the code provided was {response_message.get('function_call').get('arguments')}
                The error was {ERROR}""")
                    return f"""Something went wrong, the code provided was {response_message.get('function_call').get('arguments')}
                The error was {ERROR}"""

                # Step 4: send the info on the function call and function response to GPT
                chat_history.append(response_message)  # extend conversation with assistant's reply
                chat_history.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
                second_response = openai.ChatCompletion.create(
                    model=model,
                    messages=chat_history,
                )  # get a new response from GPT where it can see the function response
                return second_response["choices"][0]["message"].get("content")

            except Exception as e:
                logging.error(f"Error {e}")
                return e

        else:
            logging.debug(response_message)
            return response_message.get("content")


    except Exception as e:
        logging.error(f"Error with OpenAI API key: {e}")
        # messagebox.showerror("Error", e)
        return e


def run_convo_pure_chat(chat_history, model, max_tokens, temperature):
    try:
        model_engine = model

        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=chat_history,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )

        response_message = response["choices"][0]["message"]

        logging.debug(response_message)
    except Exception as e:
        logging.error(f"Error: {e}")
        messagebox.showerror("Error", e)
        return "Error: " + e

    return response_message.get('content')
