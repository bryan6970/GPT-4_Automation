import datetime
import functools
import io
import json
import pprint
import sys
import threading
import tkinter as tk
import tkinter.messagebox
import traceback
import warnings
from tkinter import scrolledtext
from tkinter import ttk
from tkinter.font import Font

import gcsa
import gcsa.google_calendar as gc
import googleapiclient.errors
import openai
import requests
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
from dateutil import parser
from gcsa.event import Event

messages = []
logs = []

PATH_TO_IMAGE: str = r"../Images/GPT.png"

try:
    with open("../venv/hyperparameters.json", "r") as file:
        hyperparameters = json.load(file)
except FileNotFoundError:
    with open("../venv/hyperparameters.json", "w") as f:

        hyperparameters = {
            "model": "gpt-3.5-turbo",
            "use_python": "No",
            "include_time": "Yes",
            "max_tokens": 2000,
            "messages_in_memory": 4,
            "temperature": 1.0,
            "system_message": "",
            "openai_api_key": "",
            "path_to_OAuth_credentials": "",
            "OAuth_credentials_token_save_location": "",
            "saved": True
        }
        json.dump(hyperparameters, f)

pprint.pprint(hyperparameters)


class Skip:
    """Used for functions to return to omit second api call"""

    def __init__(self, info=None, user_info=None):
        if info and user_info is None:
            warnings.warn("info and user info are both None in Skip class")

        if user_info is None:
            user_info = info

        self.info = info
        self.user_info = user_info

    def __str__(self):
        return "Skip class"


class Bot:
    def __init__(self):
        self.ERROR = False

        # Don't find this necessary.
        self.create_events = {
            "name": "create_events",
            "description": "Create multiple gcalendar events. Returns event ids",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_summaries": {
                        "type": "array",
                        "description": "Event names",
                        "items":
                            {"type": "string"}
                    },
                    "descriptions": {
                        "type": "array",
                        "description": "descriptions of each event. Provide an array with empty strings if there is "
                                       "no suitable description.",
                        "items":
                            {"type": "string"}
                    },
                    "start_times": {
                        "type": "array",
                        "description": "Time each event starts in datetime format",
                        "items":
                            {"type": "string"}
                    },
                    "end_times": {
                        "type": "array",
                        "description": "Time that each event ends in datetime format",
                        "items":
                            {"type": "string"}
                    },
                    "all_day": {
                        "type": "array",
                        "description": "If the event is an all day type in gcalendar",
                        "items": {
                            "type": "boolean"
                        }
                    },
                },
                "required": ["event_summary", "descriptions", "start_time", "end_time", "all_day"],
            },
            "return_type": {"type": "str"}
        }

        self.gcalendar_funcs = [{
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
                "description": "Create a gcalendar event. Use this to schedule a meeting. Returns event id",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_summary": {
                            "type": "string",
                            "description": "Event name",
                        },
                        "description": {
                            "type": "string",
                            "description": "description of event. Leave as an empty string if no clear description "
                                           "is given",
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
                    "required": ["event_summary", "description", "start_time", "end_time"],
                },
                "return_type": {"type": "str"}
            },

            {
                "name": "delete_event",
                "description": "Deletes event. Returns success or failure reason",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "Event id",
                        },
                    },
                    "required": ["event_id"],
                },
                "return_type": {"type": "str"}
            },
            {
                "name": "change_event_time",
                "description": "Changes event time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "Event id",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "start time of event in datetime formate",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "end time of event in datetime format",
                        },
                    },
                    "required": ["event_id", "start_time", "end_time"],
                },
                "return_type": {"type": "str"}
            }
        ]

        self.gcalendar_availablefuncs = {"get_gcalendar_events": self.get_gcalendar_events,
                                         "search_gcalendar_events": self.search_gcalendar_events,
                                         "get_gcalendar_events_byID": self.get_gcalendar_events_byID,
                                         "create_event": self.create_event,
                                         "create_events": self.create_events
                                         }

        self.python_function = {
            "name": "python",
            "description": "runs python code with exec function. Use this for any arithmetic calculations you need to do. "
                           "Returns whatever is printed",
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

        self.python_availablefunc = {"python": self.python}

        self.functions = [

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

        self.available_functions = {
            "extract_text_from_website": self.extract_text_from_website

        }

        # raise Exception("Delete line below this")
        # self.gc = gcsa.google_calendar.GoogleCalendar()

        self.load_hyperparams()

    @staticmethod
    def _call_func(function_to_call, function_args):
        try:
            if function_args == 0:
                function_response = function_to_call()

            # elif function_args == 1:
            #     function_response = function_to_call()

            else:
                function_response = function_to_call(**function_args)

            append_log(function_to_call.__name__ + " args:", function_args)
            append_log(function_to_call.__name__, function_response.__str__)
            return function_response
        except Exception as e:
            append_log("Unknown error with calling func", traceback.format_exc())
            return Skip(f"Unknown error with calling func.",
                        f"Unknown error with calling func {function_to_call.__name__}. This is a code issue and not an AI issue.")

    if True:

        @staticmethod
        def _log_call(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                caller_name = func.__name__
                logs.append(f"Func {caller_name} called in {type(self).__name__}")

                print(f"Func {caller_name} called in {type(self).__name__}")
                return func(self, *args, **kwargs)

            return wrapper

        @_log_call
        def python(self, code):
            try:

                # Redirect the standard output to a StringIO object
                output = io.StringIO()
                sys.stdout = output

                # Execute the code using exec()
                exec(code)

                # Restore the standard output
                sys.stdout = sys.__stdout__

                # Get the output from the StringIO object
                return output.getvalue()
            except Exception as e:
                return Skip(f"Error is python string: {e}", "Error with AI generated code")

        @_log_call
        def extract_text_from_website(self, url):

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

                    return extracted_text

                else:
                    return Skip(f"Error: Failed to retrieve content from {url}")
            except Exception as e:

                return e

        def _string_to_date(self, input_string):
            try:
                # Parse the input string using dateutil.parser
                datetime_object = parser.parse(input_string)

                return datetime_object
            except ValueError as e:
                # Handle parsing errors gracefully
                print(f"Error with time format {input_string}", file=sys.stderr)
                return str(e)

        @_log_call
        def init_gc(self, creds_path, token_path):
            self.gc = gcsa.google_calendar.GoogleCalendar(credentials_path=creds_path,
                                                          token_path=token_path)
            return self.gc

        def _parse(self, events):
            return [f"Event: {event.summary}. ID: {event.id}. Start time: {event.start}. End time: {event.end}" for
                    event in events]

        @_log_call
        def get_gcalendar_events(self, necessary_events):
            if necessary_events > 50:
                necessary_events = 50
            return str(self._parse(gc.get_events(order_by="startTime", single_events=True))[:necessary_events])

        @_log_call
        def search_gcalendar_events(self, search_key, necessary_events=None):
            if necessary_events is None:
                append_log("Parameter not filled", "necessary_events parameter not filled")
                return str(self._parse(self.gc.get_events(query=search_key))[
                           :10]) + "\n Precaution: necessary_events parameter was not filled. Search still worked"

            if necessary_events > 50:
                necessary_events = 50

            return str(self._parse(self.gc.get_events(query=search_key))[:necessary_events])

        @_log_call
        def get_gcalendar_events_byID(self, ID):
            return str(self.gc.get_event(ID))

        @_log_call
        def create_event(self, event_summary, description, start_time, end_time, all_day=False, default_reminders=True):
            # ChatGPT has no access to default reminders parameter

            start, end = self._string_to_date(start_time), self._string_to_date(end_time)

            if all_day:
                start = start.date()
                end = end.date()

            event = Event(event_summary, description=description, default_reminders=default_reminders,
                          start=start,
                          end=end)

            event = self.gc.add_event(event)

            if event.start.date() == event.end.date():

                return Skip(
                    f"Event {event.summary} created. Starts at {event.start.strftime('%d %b, %I:%M%p, on %A')},"
                    f" ends at {event.end.strftime('%d %b, %I:%M%p, on %A')}. Event ID is {event.id}",

                    f"System: {event.summary} scheduled from {event.start.strftime('%d %b, %I:%M%p, on %A')} "
                    f"to {event.end.strftime('%d %b, %I:%M%p, on %A')}")
            else:
                return Skip(
                    f"Event {event.summary} created. Starts at {event.start.strftime('%d %b, %I:%M%p, on %A')},"
                    f" ends at {event.end.strftime('%d %b, %I:%M%p, on %A')}. Event ID is {event.id}",

                    f"System: {event.summary} scheduled on {event.start.strftime('%d %b, %I:%M%p, on %A')} from"
                    f" {event.start.strftime('%I%p')} to {event.end.strftime('%I%p')}")

        @_log_call
        def create_events(self, event_summaries, descriptions, start_times, end_times, all_day: list,
                          default_reminders=True):
            # ChatGPT has no access to default reminders parameter
            raise NotImplementedError

            if len(event_summaries) == len(start_times) == len(end_times) == len(all_day) == len(descriptions):
                start_times_ = []
                end_times_ = []
                for start_time, end_time in zip(start_times, end_times):
                    start_times_.append(self._string_to_date(start_time))
                    end_times_.append(self._string_to_date(end_time))

                event_ids = []
                error_events = []

                for i in range(len(event_summaries)):
                    try:
                        if all_day:
                            start = start_times_[i].date()
                            end = end_times_[i].date()
                        else:
                            start = start_times_[i]
                            end = end_times_[i]

                        event = Event(event_summaries[i], description=descriptions[i],
                                      default_reminders=default_reminders,
                                      start=start,
                                      end=end)

                        event_ids.append(
                            f"Event: {event_summaries[i]}\nEvent ID: {self.gc.add_event(event).id}")
                    except Exception as e:
                        error_events.append(f"Error with {event_summaries[i]}.")
                        print("DEBUG: " + e.__str__())

                if not error_events:

                    return "Events created. Info:\n " + event_ids.__str__()
                else:
                    return "Events created. Info:\n " + event_ids.__str__() + "Events with errors: " + error_events.__str__()

            else:
                return "All parameters must be the same length"

        @_log_call
        def delete_event(self, event_id):
            try:
                event = self.gc.get_event(event_id)
                event_summary = event.summary

                self.gc.delete_event(event_id)
                return Skip("Event was deleted", f"Event {event_summary}  was deleted")
            except googleapiclient.errors.HttpError as e:
                append_log("Error contacting G calendar", e)
                return Skip(f"Error: {e.reason}", "Error contacting G calendar")

        @_log_call
        def change_event_time(self, event_id, start_time, end_time):
            event = self.gc.get_event(event_id=event_id)
            event.start = self._string_to_date(start_time)
            event.end = self._string_to_date(end_time)
            self.gc.update_event(event=event)

            return Skip(f"Event {event.summary} moved to start at {start_time} and end at {end_time}")

    @_log_call
    def load_hyperparams(self):
        with open("../venv/hyperparameters.json", "r") as f:
            hyperparameters = json.load(f)

        openai.api_key = hyperparameters["openai_api_key"]

        try:
            self.gc = self.init_gc(hyperparameters["path_to_OAuth_credentials"],
                                   hyperparameters["OAuth_credentials_token_save_location"])
        except Exception:
            self.gc = None

        if self.gc:
            for func in self.gcalendar_funcs:
                self.functions.append(func)

            self.available_functions.update(self.gcalendar_availablefuncs)

        if hyperparameters["use_python"].lower() == "yes":
            self.functions.append(self.python_function)

            self.available_functions.update(self.python_availablefunc)

    def _get_last_few_msgs(self, message):
        message_ = message[-hyperparameters["messages_in_memory"]:]

        if not message_:
            return message
        else:
            return message_

    def run_convo(self, model, max_tokens, temperature):

        model_engine = model

        try:

            response = openai.ChatCompletion.create(
                model=model_engine,
                messages=self._get_last_few_msgs(messages),
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=temperature,
                functions=self.functions,
                function_call="auto"
            )

        except openai.error.AuthenticationError as e:
            append_log("Authentication Error", e)
            print(e.user_message)
            tkinter.messagebox.showerror("Error", e.user_message)
            return None

        response_message = response["choices"][0]["message"]

        # Step 2: check if GPT wanted to call a function
        if response_message.get("function_call"):
            try:
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors
                # only one function in this example, but you can have multiple

                function_name = response_message["function_call"]["name"]
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])

                print(f"AI called function {function_name}", file=sys.stderr)

                # Call the function that the AI wants to call
                function_response = self._call_func(function_to_call, function_args)

                # if function response was a message to be returned to chat, return it
                if isinstance(function_response, Skip):
                    append_info_message(function_response.info)
                    display_message(function_response.user_info)
                    return function_response

                # Step 4: send the info on the function call and function response to GPT
                append_func_response(function_name, function_response)

                second_response = openai.ChatCompletion.create(
                    model=model,
                    messages=self._get_last_few_msgs(messages),
                )  # get a new response from GPT where it can see the function response

                return second_response["choices"][0]["message"].get("content")

            except Exception as e:
                append_log("Error in function calling", e)

                return f"Error:\n {e}"

        else:
            pprint.pprint(self._get_last_few_msgs(messages))
            if self.ERROR:
                return response_message.get("content")
            return response_message.get("content")


Bot = Bot()


def append_func_response(func_name, response):
    messages.append({"role": "function", "name": func_name, "content": response})
    return {"role": "function", "name": func_name, "content": response}


def append_log(log_name, details):
    logs.append({log_name: details})


def append_info_message(content):
    messages.append({"role": "information", "content": content})


def commands(command) -> None:
    global messages
    if command.lower() == "$chat_history" or command.lower() == "$chathistory":

        pprint.pprint(messages)
        display_message(pprint.pformat(messages))

    elif command.lower() == "$hyperparams" or command.lower() == "$hyperparameters":
        pprint.pprint(hyperparameters)

    elif command.lower() == "$logs":
        pprint.pprint(logs)
        display_message(pprint.pformat(logs))

    elif command.lower() == "$clear":
        messages = []
        chat_area.configure(state='normal')  # Enable editing
        chat_area.delete("1.0", tk.END)
        chat_area.see(tk.END)  # Auto scroll to the latest message
        chat_area.configure(state='disabled')  # Disable editing

    else:
        display_message(f"{command} is not a command")

    input_text.delete("1.0", tk.END)  # Clear the input text


def bot_response() -> None:
    # Get bot response
    bot_reply = Bot.run_convo(hyperparameters["model"],
                              hyperparameters["max_tokens"],
                              hyperparameters["temperature"])
    # Remove the "Loading..." message
    remove_chat_message()
    if not isinstance(bot_reply, Skip):
        messages.append({"role": "assistant", 'content': bot_reply})

        # Display the bot response in the chat area
        display_message(f"\nBot: {bot_reply}")
    else:
        display_message(f"\n{bot_reply.user_info}")


def open_hyperparameters_window() -> None:
    global hyperparameters

    def save_hyperparameters(by_user=True) -> None:
        global hyperparameters
        # Get selected hyperparameters from the UI
        selected_model: str = model_combobox.get()
        use_python: str = use_python_combobox.get()
        include_time: str = include_time_combobox.get()
        max_tokens: int = int(max_tokens_entry.get())
        messages_in_memory: int = int(messages_in_memory_entry.get())
        temperature: float = float(temperature_entry.get())
        system_message: str = system_message_text.get("1.0", tk.END)
        openai_api_key: str = openai_api_key_entry.get()
        path_to_OAuth_credentials: str = path_to_OAuth_credentials_entry.get()
        OAuth_credentials_token_save_location: str = OAuth_credentials_token_save_location_entry.get()

        # Save the hyperparameters
        hyperparameters = {
            "model": selected_model,
            "use_python": use_python,
            "include_time": include_time,
            "max_tokens": max_tokens,
            "messages_in_memory": messages_in_memory,
            "temperature": temperature,
            "system_message": system_message,
            "openai_api_key": openai_api_key,
            "path_to_OAuth_credentials": path_to_OAuth_credentials,
            "OAuth_credentials_token_save_location": OAuth_credentials_token_save_location,
            "saved": True
        }

        with open("../venv/hyperparameters.json", "w") as f:
            json.dump(hyperparameters, f)

        Bot.load_hyperparams()

        if by_user:
            on_closing(saved=True)

    def on_closing(saved=False):
        if not saved:
            save_hyperparameters(by_user=False)

        # After the window is closed, display the messages
        if hyperparameters["saved"]:
            display_message("System: Hyperparameters loaded!")
        else:
            display_message("System: Hyperparameters were not saved!")

        hyperparameters["saved"] = False

        window.destroy()

    def set_appropriate_max_token(event: tk.Event) -> None:
        # Delete old tokens
        max_tokens_entry.delete(0, tk.END)

        # Set max tokens based on the selected model
        model = model_combobox.get()

        if model == "gpt-3.5-16k":
            max_tokens_entry.insert(0, "6000")
        elif model == "gpt-4":
            max_tokens_entry.insert(0, "3000")
        elif model == "gpt-3.5-turbo":
            max_tokens_entry.insert(0, "2000")
        elif model == "gpt-4-32k":
            max_tokens_entry.insert(0, "10000")
        else:
            max_tokens_entry.insert(0, hyperparameters["max_tokens"])

    if True:
        # Create the hyperparameters window
        window = tk.Toplevel(root)
        window.title("Hyperparameters")
        window.configure(background="#1C1C1C")

        roboto_font_ = Font(family="Roboto", size=10)

        # Create a custom style for the widgets
        # Configure the style for labels, buttons, and entries
        _style_ = ttk.Style()

        _style_.configure("TLabel", background="#1C1C1C", foreground="white")

        # Model selection
        model_label = ttk.Label(window, font=roboto_font_, text="Model:")
        model_label.grid(row=0, column=0, sticky="w")
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]
        model_combobox = ttk.Combobox(window, font=roboto_font_, values=models, state="readonly")
        model_combobox.current(models.index(hyperparameters["model"]))
        model_combobox.bind("<<ComboboxSelected>>", set_appropriate_max_token)
        model_combobox.grid(row=0, column=1, padx=(10, 0), sticky="w")

        # Use python
        use_python_label = ttk.Label(window, font=roboto_font_, text="Use python?:")
        use_python_label.grid(row=1, column=0, sticky="w")
        use_python_options = ["Yes", "No"]
        use_python_combobox = ttk.Combobox(window, font=roboto_font_, values=use_python_options, state="readonly")
        use_python_combobox.current(use_python_options.index(hyperparameters["use_python"]))
        use_python_combobox.grid(row=1, column=1, padx=(10, 0), sticky="w")

        # Include time
        include_time_label = ttk.Label(window, font=roboto_font_, text="Include Time?:")
        include_time_label.grid(row=2, column=0, sticky="w")
        include_time_options = ["Yes", "No"]
        include_time_combobox = ttk.Combobox(window, font=roboto_font_, values=include_time_options, state="readonly")
        include_time_combobox.current(include_time_options.index(hyperparameters["include_time"]))
        include_time_combobox.grid(row=2, column=1, padx=(10, 0), sticky="w")

        # Maximum tokens
        max_tokens_label = ttk.Label(window, font=roboto_font_, text="Max response Tokens:")
        max_tokens_label.grid(row=3, column=0, sticky="w")
        max_tokens_entry = tk.Entry(window, font=roboto_font_, fg="White", bg="black", insertbackground="white")
        max_tokens_entry.insert(0, hyperparameters["max_tokens"])
        max_tokens_entry.grid(row=3, column=1, padx=(10, 0), sticky="w")

        # Messages in memory
        messages_in_memory_label = ttk.Label(window, font=roboto_font_, text="Messages in memory:")
        messages_in_memory_label.grid(row=4, column=0, sticky="w")
        messages_in_memory_entry = tk.Entry(window, font=roboto_font_, fg="White", bg="black", insertbackground="white")
        messages_in_memory_entry.insert(0, hyperparameters["messages_in_memory"])
        messages_in_memory_entry.grid(row=4, column=1, padx=(10, 0), sticky="w")

        # Temperature
        temperature_label = ttk.Label(window, font=roboto_font_, text="Temperature:")
        temperature_label.grid(row=5, column=0, sticky="w")
        temperature_entry = tk.Entry(window, font=roboto_font_, fg="White", bg="black", insertbackground="white")
        temperature_entry.insert(0, hyperparameters["temperature"])
        temperature_entry.grid(row=5, column=1, padx=(10, 0), sticky="w")

        # System message
        system_message_label = ttk.Label(window, font=roboto_font_, text="System message:")
        system_message_label.grid(row=6, column=0, sticky="w")
        system_message_text: tk.Text = tk.Text(window, font=roboto_font_, height=1, fg="White", bg="black",
                                               insertbackground="white")
        system_message_text.insert("1.0", hyperparameters["system_message"][:-1])
        system_message_text.grid(row=6, column=1, padx=(10, 0), sticky="news")

        # OpenAI api key
        openai_api_key_label = ttk.Label(window, font=roboto_font_, text="OpenAI API key")
        openai_api_key_label.grid(row=9, column=0, sticky="w")
        openai_api_key_entry = tk.Entry(window, font=roboto_font_, fg="White", bg="black", insertbackground="white")
        openai_api_key_entry.insert(0, hyperparameters["openai_api_key"])
        openai_api_key_entry.grid(row=9, column=1, padx=(10, 0), sticky="news")

        # Path to OAuth credentials
        path_to_OAuth_credentials_label = ttk.Label(window, font=roboto_font_, text="Path to OAuth credentials:")
        path_to_OAuth_credentials_label.grid(row=10, column=0, sticky="w")
        path_to_OAuth_credentials_entry: tk.Entry = tk.Entry(window, font=roboto_font_, fg="White", bg="black",
                                                             insertbackground="white")
        path_to_OAuth_credentials_entry.insert(0, hyperparameters["path_to_OAuth_credentials"])
        path_to_OAuth_credentials_entry.grid(row=10, column=1, padx=(10, 0), sticky="news")

        # OAuth's credentials token save location
        OAuth_credentials_token_save_location_label = ttk.Label(window, font=roboto_font_,
                                                                text="OAuth credentials token save location:")
        OAuth_credentials_token_save_location_label.grid(row=11, column=0, sticky="w")
        OAuth_credentials_token_save_location_entry: tk.Entry = tk.Entry(window, font=roboto_font_, fg="White",
                                                                         bg="black", insertbackground="white")
        OAuth_credentials_token_save_location_entry.insert(0, hyperparameters["OAuth_credentials_token_save_location"])
        OAuth_credentials_token_save_location_entry.grid(row=11, column=1, padx=(10, 0), sticky="news")

        # Save button
        save_button = tk.Button(window, text="Save", command=save_hyperparameters, fg="White", bg="black")
        save_button.grid(row=12, column=0, columnspan=2, pady=(20, 0))

        # Configure row and column weight to make text boxes expand
        window.grid_rowconfigure(11, weight=1)
        window.grid_columnconfigure(1, weight=1)

        # Protocol when the window is closed
        window.protocol("WM_DELETE_WINDOW", on_closing)

        window.mainloop()

    if True:
        _root_ = tk.Toplevel(root)
        style = ttk.Style()

        btn = ttk.Button(_root_, text="Sample")

        style.map('TButton', background=[('active', 'black')])
        btn.grid()

        _root_.mainloop()


def send_message(event: tk.Event = None) -> None:
    # 8 is when the enter key is being pressed
    if event.state != 8:
        return None

    message: str = input_text.get("1.0", tk.END).strip()
    if not message:
        return None

    if message.startswith("$"):
        commands(message)
    else:
        # Display the user message in the chat area
        display_message(f"You: {message}")

        if hyperparameters["include_time"].lower() == "yes":

            messages.append({'role': 'user',
                             'content': message + f"\n Time is {datetime.datetime.now().strftime('%A,%Y-%m-%d %H:%M')}"})
        else:
            messages.append({'role': 'user',
                             'content': message})

        # Display "Loading..." message
        loading_message = display_message("Bot: Loading...")

        # Get bot response in a separate thread
        threading.Thread(target=bot_response).start()

        input_text.delete("1.0", tk.END)  # Clear the input text


def set_border_color(event: tk.Event) -> None:
    input_text.config(highlightbackground="#282828")


def unset_border_color(event: tk.Event) -> None:
    input_text.config(highlightbackground="#1C1C1C")


def superscript(text):
    raise NotImplementedError
    result = []
    i = 0
    while i < len(text):
        if text[i] == '^' and i + 1 < len(text) and text[i + 1] != ' ':
            superscripted = ''
            i += 1  # Skip the '^' character
            while i < len(text) and text[i] != ' ':
                superscripted += text[i]
                i += 1
            result.append(f'<sup>{superscripted}</sup>')
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


def display_message(message: str) -> tk.Text:
    chat_area.configure(state='normal')  # Enable editing

    chat_area.insert(tk.END, message + "\n\n")
    chat_area.see(tk.END)  # Auto scroll to the latest message
    chat_area.configure(state='disabled')  # Disable editing

    return chat_area


def remove_chat_message() -> None:
    chat_area.configure(state='normal')  # Enable editing
    chat_area.delete('end-3l', 'end')  # Delete the third-to-last line
    chat_area.configure(state='disabled')  # Disable editing


def delete_word(event):
    # Get the current cursor position
    cursor_position = input_text.index(tk.INSERT)

    if event.keysym == "BackSpace":
        # Delete the word before the cursor
        input_text.delete("insert-1c wordstart", cursor_position)
    elif event.keysym == "Delete":
        # Delete the word before the cursor
        input_text.delete(cursor_position, "insert-1c wordend")


if __name__ == '__main__':
    # Create the main window
    root: tk.Tk = tk.Tk()
    root.title("Chat App")
    root.configure(background="#1C1C1C")

    # Change the DPI scaling factor
    style = tk.ttk.Style()
    style.configure(".", dpi=144)  # You can adjust the DPI value as needed

    arial_font = Font(family="Arial", size=8)
    segoe_UI_font = Font(family="Segoe UI", size=10)
    code_font = Font(family="Monospace", size=10)

    # Set the window logo
    logo_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(PATH_TO_IMAGE))
    root.iconphoto(True, logo_image)

    # Create a frame to hold the chat area
    chat_frame: tk.Frame = tk.Frame(root, bg="#1C1C1C")
    chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # Create a scrolled text widget for the chat area
    chat_area: scrolledtext.ScrolledText = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, font=segoe_UI_font,
                                                                     bg="#1C1C1C", fg="#EFEFEF",
                                                                     width=50,
                                                                     height=20)

    chat_area.configure(state='disabled')  # Make the chat area read-only
    chat_area.pack(fill="both", expand=True)

    # Create a frame to hold the input text and send button
    input_frame: tk.Frame = tk.Frame(root, bg="#282828")
    input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    # Create an input text widget
    input_text: tk.Text = tk.Text(input_frame, wrap=tk.WORD, font=segoe_UI_font, bg="#282828", fg="#FFFFFF",
                                  height=2)

    # Add a vertical scrollbar
    scrollbar = tk.Scrollbar(input_frame, command=input_text.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Configure the Text widget to use the scrollbar
    input_text.configure(yscrollcommand=scrollbar.set)

    input_text.bind("<FocusIn>", set_border_color)  # Set border color on focus
    input_text.bind("<FocusOut>", unset_border_color)  # Unset border color when focus is lost
    input_text.bind("<Return>", send_message)  # Send message on Enter key

    # Bind Ctrl + Backspace and Ctrl + Delete to delete the whole word
    input_text.bind("<Control-BackSpace>", delete_word)
    input_text.bind("<Control-Delete>", delete_word)

    max_lines = 20  # max lines that the text box can go to
    # Increase textbox size with text
    input_text.bind("<Key>", lambda event: input_text.configure(
        height=min(max(2, int(input_text.index('end-1c').split('.')[0])), max_lines)))

    # Change the color of the text indicator to white
    input_text.configure(insertbackground="#FFFFFF", highlightthickness=0)
    input_text.grid(row=0, column=0, sticky="ew")

    # Configure column weight to make it scale with window size
    input_frame.grid_columnconfigure(0, weight=1)

    # Create the "hyper params" button
    hyper_button: tk.Button = tk.Button(root, font=arial_font, text="Edit hyperparameters",
                                        command=open_hyperparameters_window,
                                        bg="#282828",
                                        fg="#FFFFFF", activebackground="#1C1C1C", activeforeground="#FFFFFF")
    hyper_button.place(relx=1, rely=0, anchor="ne", x=-10, y=10)

    # Configure the chat frame to scale when window is resized
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    root.mainloop()
