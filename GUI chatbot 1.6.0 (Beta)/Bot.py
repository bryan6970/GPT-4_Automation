import datetime
import json
import os
import logging
import sys

import openai
from tkinter import messagebox

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
from dateutil import parser

# Configure logging level
logging.basicConfig(filename="logs.log", level=logging.DEBUG)
if True:

    try:
        openai.api_key = os.environ.get("OPEN_AI_API_KEY")
    except Exception as e:
        print(f"Error setting OpenAI API key: {e}", file=sys.stderr)
        messagebox.showerror("Error", "Failed to set OpenAI API key. Ensure that the OpenAI API key is under "
                                      "OPEN_AI_API_KEY in your system environment variables, "
                                      "and then restart your computer")
        sys.exit()

    try:
        with open(os.environ.get("Calendar_creds"), 'r') as f:
            calendar_creds_json = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", "Calendar_creds not found in PATH. Please fill with JSON details. Get details "
                                      "from console.google.com, and restart your computer")
        sys.exit()

ERROR = False

with open("hyperparameters.json", "r") as file:
    hyperparameters = json.load(file)


def load_hyperparams():
    global hyperparameters
    with open("hyperparameters.json", "r") as f:
        hyperparameters = json.load(f)


def run_python_code(code):
    global ERROR
    try:
        exec(code)
    except Exception as e:
        logging.debug(e)
        ERROR = e
        return e


def extract_text_from_website(url):
    global ERROR
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
        ERROR = e
        return e


def get_datetime():

    time_ = str( datetime.datetime.now())
    return time_


def _string_to_rfc3339(input_string):
    try:
        # Parse the input string using dateutil.parser
        datetime_object = parser.parse(input_string)

        # Convert the datetime object to RFC3339 format
        rfc3339_format = datetime_object.isoformat()

        return rfc3339_format
    except ValueError as e:
        # Handle parsing errors gracefully
        print(f"Error with time format {input_string}", file=sys.stderr)
        return str(e)


def get_existing_event_info(start_time, end_time):
    # Load credentials
    creds = service_account.Credentials.from_service_account_info(
        calendar_creds_json, scopes=['https://www.googleapis.com/auth/calendar']
    )

    # Create a service object to interact with the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # Define the time window for the query
    start_time = _string_to_rfc3339(start_time)
    end_time = _string_to_rfc3339(end_time)

    # Query the calendar for events in the specified time window
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if events:
        msg = ""

        # If there are events, return information about the first event found
        for event in events:
            event_name = event['summary']
            event_start = event['start']['dateTime']
            event_end = event['end']['dateTime']
            msg = msg + f"Conflict. Name: '{event_name}' Start time {event_start} end time {event_end}"
        return msg
    else:
        # If no events were found, return None
        return "No events were found"


def create_google_calendar_event(name, start_time, end_time, check_conflict=True):
    if check_conflict:
        conflict_info = get_existing_event_info(start_time, end_time)
    else:
        conflict_info = False

    if conflict_info and conflict_info != "No events were found":
        return f"Event not created {conflict_info}. To bypass, set check_conflict to False"

    # Load credentials
    creds = service_account.Credentials.from_service_account_info(
        calendar_creds_json, scopes=['https://www.googleapis.com/auth/calendar']
    )

    # Create a service object to interact with the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # Convert start_time and end_time to RFC3339 format
    start_time = _string_to_rfc3339(start_time)
    end_time = _string_to_rfc3339(end_time)

    # Create the event
    time_zone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()
    event = {
        'summary': name,
        'start': {'dateTime': start_time, 'timeZone': time_zone},
        'end': {'dateTime': end_time, 'timeZone': time_zone},
    }

    # Insert the event into the calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    return f'Event created: f{event.get("htmlLink")}'


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
        "name": "create_google_calendar_event",
        "description": "Create a google calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of event",
                },
                "start_time": {
                    "type": "string",
                    "description": "start time in RFC3339 format",
                },
                "end_time": {
                    "type": "string",
                    "description": "end time in RFC3339 format",
                },
                "check_conflict": {
                    "type": "boolean",
                    "description": "To check conflict with other events. True to check conflict.",
                },
            },
            "required": ["name", "start_time", "end_time"],
        },
        "return_type": {"type": "str"}
    },
    {
        "name": "get_existing_event_info",
        "description": "get events in time range  from google calendar",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "start time in RFC3339 format",
                },
                "end_time": {
                    "type": "string",
                    "description": "end time in RFC3339 format",
                }
            },
            "required": ["start_time", "end_time"],
        },
        "return_type": {"type": "str"}
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
    }, {"name": "get_datetime",
        "description": "Get current datetime",
        "parameters": {
            "type": "object",
            "properties": {
            },
        },

        "return_type": {"type": "str"}}]

functions_without_python = functions[1:]

available_functions = {
    "run_python_code": run_python_code,
    "extract_text_from_website": extract_text_from_website,
    "get_datetime": get_datetime,
    "get_existing_event_info": get_existing_event_info,
    "create_google_calendar_event": create_google_calendar_event

}

available_functions_without_python = {"extract_text_from_website": extract_text_from_website,
                                      "get_datetime": get_datetime,
                                      "get_existing_event_info": get_existing_event_info,
                                      "create_google_calendar_event": create_google_calendar_event

                                      }


def _call_func(function_name, function_to_call, function_args, response_message):

    if function_name == "run_python_code":
        return f"Success! The code provided was  {response_message.get('function_call').get('arguments')}"

    elif function_args is not True:
        function_response = function_to_call()

    else:
        function_response = function_to_call(**function_args)

    return function_response


def _check_error(response_message):
    if ERROR:
        logging.debug(
            f"""Something went wrong, the code provided was {response_message.get('function_call').get('arguments')}
      The error was {ERROR}""")
        return f"""Something went wrong, the code provided was {response_message.get('function_call').get('arguments')}
      The error was {ERROR}"""
    else:
        logging.debug(
            f"Success! The input for the parameter provided was  {response_message.get('function_call').get('arguments')}")
        return f"Success! The input for the parameter provided was  {response_message.get('function_call').get('arguments')}"


def run_convo_with_function_calls(chat_history, model, max_tokens, temperature, use_python):
    try:
        if use_python.lower() == "yes":
            pass
        else:
            available_functions = available_functions_without_python
            functions = functions_without_python

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

                # Call the function that the AI wants to call
                function_response = _call_func(function_name, function_to_call, function_args, response_message)

                return function_response

            except Exception as e:
                logging.error(f"Error: {e}")
                # messagebox.showerror("Error", e)
                print(e, file=sys.stderr)
                return e


        else:
            logging.debug(response_message)
            return response_message.get("content")


    except Exception as e:
        logging.error(f"Error with OpenAI API key: {e}")
        # messagebox.showerror("Error", e)
        return e


def run_convo_with_function_calls_and_explanation(chat_history, model, max_tokens, temperature, use_python):
    global functions

    if use_python.lower() == "yes":
        available_functions_ = available_functions
    else:
        available_functions_ = available_functions_without_python
        functions = functions_without_python

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
            # only one function in this example, but you can have multiple

            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions_[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])

            # Call the function that the AI wants to call
            function_response = _call_func(function_name, function_to_call, function_args, response_message)

            # if function response was a message to be returned to chat, return it
            if function_response == "(Developer) No function name has been declared, unable to pass args":
                return function_response

            # Step 4: send the info on the function call and function response to GPT
            # chat_history.append(response_message)  # extend conversation with assistant's reply
            chat_history.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response

            print(chat_history)

            second_response = openai.ChatCompletion.create(
                model=model,
                messages=chat_history,
            )  # get a new response from GPT where it can see the function response

            logging.debug(second_response)

            return second_response["choices"][0]["message"].get("content")

        except Exception as e:

            raise e

    else:
        logging.debug(response_message)
        if ERROR:
            return response_message.get("content") + _check_error(response_message)
        return response_message.get("content")




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
