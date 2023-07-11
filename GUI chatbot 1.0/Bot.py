import json
import os
import logging
import sys

import openai
from tkinter import messagebox

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


def run_convo_with_function_calls(chat_history, model, max_tokens, temperature):
    try:
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
        }]

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

                available_functions = {
                    "run_python_code": run_python_code,
                }
                # only one function in this example, but you can have multiple

                function_name = response_message["function_call"]["name"]
                function_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])
                function_response = function_to_call(
                    code=function_args.get("code")
                )

                # Step 4: send the info on the function call and function response to GPT
                # messages.append(response_message)  # extend conversation with assistant's reply

            except Exception as e:
                logging.error(f"Error with OpenAI API key: {e}")
                messagebox.showerror("Error", e)
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
        messagebox.showerror("Error", e)
        return e


def run_convo_with_function_calls_and_explanation(chat_history, model, max_tokens, temperature):
    try:
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
        }]

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

                available_functions = {
                    "run_python_code": run_python_code,
                }
                # only one function in this example, but you can have multiple

                function_name = response_message["function_call"]["name"]
                function_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])
                function_response = function_to_call(
                    code=function_args.get("code")
                )

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
                return second_response

            except Exception as e:
                logging.error(f"Error with OpenAI API key: {e}")
                messagebox.showerror("Error", e)
                return e

        else:
            logging.debug(response_message)
            return response_message.get("content")


    except Exception as e:
        logging.error(f"Error with OpenAI API key: {e}")
        messagebox.showerror("Error", e)
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
        logging.error(f"Error with OpenAI API key: {e}")
        messagebox.showerror("Error", e)
        return e

    return response_message.get('content')
