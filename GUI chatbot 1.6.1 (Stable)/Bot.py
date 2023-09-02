import datetime
import json
import logging
import pprint
import sys

import gcsa
import gcsa.google_calendar as gc
import openai
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from gcsa.event import Event

import main

ERROR = False


def _call_func(function_name, function_to_call, function_args, response_message):
    if function_name == "run_python_code":
        return f"Success! The code provided was  {response_message.get('function_call').get('arguments')}"

    elif function_args == 0:
        function_response = function_to_call()

    # elif function_args == 1:
    #     function_response = function_to_call()

    else:
        function_response = function_to_call(**function_args)

    return function_response


if True:

    def python(code):
        global ERROR
        try:
            exec(code)
            return "Code ran successfully"
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
        time_ = str(datetime.datetime.now())
        return time_


    def _string_to_date(input_string):
        try:
            # Parse the input string using dateutil.parser
            datetime_object = parser.parse(input_string)

            return datetime_object
        except ValueError as e:
            # Handle parsing errors gracefully
            print(f"Error with time format {input_string}", file=sys.stderr)
            return str(e)


    def init_gc(creds_path, token_path):
        global gc
        gc = gcsa.google_calendar.GoogleCalendar(credentials_path=creds_path,
                                                 token_path=token_path)
        return gc


    def _include_id(events):
        return [str(event) + " <ID: " + event.id + ">" for event in events]


    def get_gcalendar_events(necessary_events):
        if necessary_events > 50:
            necessary_events = 50
        return str(_include_id(gc.get_events(order_by="startTime", single_events=True))[:necessary_events])


    def search_gcalendar_events(search_key, necessary_events):
        if necessary_events > 50:
            necessary_events = 50
        return str(_include_id(gc.get_events(query=search_key))[:necessary_events])


    def get_gcalendar_events_byID(ID):
        return str(gc.get_event(ID))


    def create_event(event_summary, start_time, end_time, all_day=False):
        start, end = _string_to_date(start_time), _string_to_date(end_time)

        if all_day:
            event = Event(event_summary,
                          start=start.date(),
                          end=end_time.date())
        else:
            event = Event(event_summary,
                          start=start,
                          end=end)

        event = gc.add_event(event)

        return "Event created successfully. ID: " + event.id


    def create_events(event_summaries, start_times, end_times, all_day: list):
        if len(event_summaries) == len(start_times) == len(end_times) == len(all_day):
            start_times = [_string_to_date(time) for time in start_times]
            end_times = [_string_to_date(time for time in end_times)]

            event_ids = []
            error_events = []

            for i in range(len(event_summaries)):
                try:
                    if all_day[i]:
                        event = Event(event_summaries[i],
                                      start=start_times[i].date(),
                                      end=end_times[i].date())
                    else:
                        event = Event(event_summaries[i],
                                      start=start_times[i],
                                      end=end_times[i])

                    event_ids.append(f"Event Summary: {event_summaries[i]}\nEvent ID: {gc.add_event(event).id}")
                except Exception as e:
                    error_events.append(f"Error with {event_summaries[i]}.")
                    print("DEBUG: " + e.__str__())

            if not error_events:

                return "Events created. Info:\n " + event_ids.__str__()
            else:
                return "Events created. Info:\n " + event_ids.__str__() + "Events with errors: " + error_events.__str__()

        else:
            return "All parameters must be the same length"

gcalendar_funcs = [{
    "name": "get_gcalendar_events",
    "description": "gets most recent gcalendar events. Returns list of events.",
    "parameters": {
        "type": "object",
        "properties": {
            "necessary_events": {
                "type": "integer",
                "description": "events needed"
            }
        },
        "required:": ["necessary_events"],
    },
    "return_type": {"type": "str"}
},
    {
        "name": "search_gcalendar_events",
        "description": "search for an event in gcalendar with a string. IDs not allowed. Returns list of events.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_key": {
                    "type": "string",
                    "description": "Search key"
                },
                "necessary_events": {
                    "type": "integer",
                    "description": "events needed"
                }
            },
            "required:": ["search_key"],
        },
        "return_type": {"type": "str"}
    },
    {
        "name": "get_gcalendar_events_byID",
        "description": "search for an event in gcalendar with ID. Returns event.",
        "parameters": {
            "type": "object",
            "properties": {
                "ID": {
                    "type": "string",
                    "description": "Event ID"
                }
            },
            "required:": ["ID"],
        },
        "return_type": {"type": "str"}
    },
    {
        "name": "create_event",
        "description": "Create a gcalendar event. Returns event id",
        "parameters": {
            "type": "object",
            "properties": {
                "event_summary": {
                    "type": "string",
                    "description": "Event name",
                },
                "start_time": {
                    "type": "string",
                    "description": "Time that event starts in datetime format",
                },
                "end_time": {
                    "type": "string",
                    "description": "Time that event ends in datetime format",
                },
                "all_day": {
                    "type": "boolean",
                    "description": "If the event is an all day type in gcalendar",
                },
            },
            "required": ["event_summary", "start_time", "end_time"],
        },
        "return_type": {"type": "str"}
    },
    {
        "name": "create_events",
        "description": "Create multiple gcalendar events. Returns event ids",
        "parameters": {
            "type": "object",
            "properties": {
                "event_summaries": {
                    "type": "list",
                    "description": "Event names",
                    "items":
                        {"type": "string"}
                },
                "start_time": {
                    "type": "list",
                    "description": "Time each event starts in datetime format",
                    "items":
                        {"type": "string"}
                },
                "end_time": {
                    "type": "list",
                    "description": "Time that each event ends in datetime format",
                    "items":
                        {"type": "string"}
                },
                "all_day": {
                    "type": "list",
                    "description": "If the event is an all day type in gcalendar",
                    "items": {
                        "type": "boolean"
                    }
                },
            },
            "required": ["event_summary", "start_time", "end_time", "all_day"],
        },
        "return_type": {"type": "str"}
    }
]

gcalendar_availablefuncs = {"get_gcalendar_events": get_gcalendar_events,
                            "search_gcalendar_events": search_gcalendar_events,
                            "get_gcalendar_events_byID": get_gcalendar_events_byID,
                            "create_event": create_event
                            }

python_function = {
    "name": "python",
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
}

python_availablefunc = {"python": python}

functions = [

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
    "extract_text_from_website": extract_text_from_website

}


def load_hyperparams():
    global hyperparameters, functions, available_functions
    with open("hyperparameters.json", "r") as f:
        hyperparameters = json.load(f)

    openai.api_key = hyperparameters["openai_api_key"]

    try:
        gc = init_gc(hyperparameters["path_to_OAuth_credentials"],
                     hyperparameters["OAuth_credentials_token_save_location"])
    except:
        gc = None

    if gc:
        for func in gcalendar_funcs:
            functions.append(func)

        available_functions.update(gcalendar_availablefuncs)

    if hyperparameters["use_python"].lower() == "yes":
        functions.append(python_function)

        available_functions.update(python_availablefunc)


def run_convo(chat_history, model, max_tokens, temperature):
    global functions

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
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])

            # Call the function that the AI wants to call
            function_response = _call_func(function_name, function_to_call, function_args, response_message)

            # if function response was a message to be returned to chat, return it
            if function_response == "Code ran successfully":
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

            main.append_func_response(function_name, function_response)

            pprint.pprint(chat_history)

            second_response = openai.ChatCompletion.create(
                model=model,
                messages=chat_history,
            )  # get a new response from GPT where it can see the function response

            logging.debug(second_response)

            return second_response["choices"][0]["message"].get("content")

        except Exception as e:

            return f"Error:\n {e}"

    else:
        logging.debug(response_message)
        if ERROR:
            return response_message.get("content")
        return response_message.get("content")


load_hyperparams()
