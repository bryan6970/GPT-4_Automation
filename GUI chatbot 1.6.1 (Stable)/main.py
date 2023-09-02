import datetime
from tkinter import scrolledtext
from PIL import ImageTk, Image
import threading
import logging
import Bot
import json
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import pprint

messages = []


def append_func_response(func_name, response):
    messages.append({"role": "function", "name": func_name, "content": response})


if __name__ == '__main__':

    # Configure logging level
    logging.basicConfig(filename="logs.log", level=logging.DEBUG)

    PATH_TO_IMAGE: str = r"../Images/GPT.png"

    with open("hyperparameters.json", "r") as file:
        hyperparameters = json.load(file)

    pprint.pprint(hyperparameters)

    spliter = "g1404018thaaou"


    def commands(command) -> None:
        if command.lower() == "$chat_history" or command.lower() == "$chathistory":

            display_message(f"Chat history: {json.dumps(messages, indent=4)}")
            pprint.pprint(messages)

        elif command.lower() == "$hyperparams" or command.lower() == "$hyperparameters":
            display_message(str(hyperparameters))
            pprint.pprint(hyperparameters)

        else:
            display_message(f"{command} is not a command")

        input_text.delete("1.0", tk.END)  # Clear the input text


    def bot_response(loading_message: tk.Text, chat_history) -> None:
        # Get bot response
        messages_ = messages[-hyperparameters["messages_in_memory"]:]

        bot_reply = Bot.run_convo(messages_, hyperparameters["model"],
                                  hyperparameters["max_tokens"],
                                  hyperparameters["temperature"])

        messages.append({"role": "assistant", 'content': bot_reply})

        # Remove the "Loading..." message
        remove_message(loading_message)

        # Display the bot response in the chat area
        display_message(f"\nBot: {bot_reply}")


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

            with open("hyperparameters.json", "w") as f:
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

            root_.destroy()

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

        # Create the hyperparameters window
        root_ = tk.Tk()
        root_.title("Hyperparameters")
        root_.configure(background="#1C1C1C")

        roboto_font_ = Font(family="Roboto", size=10)

        # Create a frame to hold the hyperparameters
        frame = ttk.Frame(root_, padding=20)
        frame.grid()

        # Model selection
        model_label = ttk.Label(frame, font=roboto_font_, text="Model:")
        model_label.grid(row=0, column=0, sticky="w")
        models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]
        model_combobox = ttk.Combobox(frame, font=roboto_font_, values=models, state="readonly")
        model_combobox.current(models.index(hyperparameters["model"]))
        model_combobox.bind("<<ComboboxSelected>>", set_appropriate_max_token)
        model_combobox.grid(row=0, column=1, padx=(10, 0), sticky="w")

        # Use python
        use_python_label = ttk.Label(frame, font=roboto_font_, text="Use python?:")
        use_python_label.grid(row=1, column=0, sticky="w")
        use_python_options = ["Yes", "No"]
        use_python_combobox = ttk.Combobox(frame, font=roboto_font_, values=use_python_options, state="readonly")
        use_python_combobox.current(use_python_options.index(hyperparameters["use_python"]))
        use_python_combobox.grid(row=1, column=1, padx=(10, 0), sticky="w")

        # Include time
        include_time_label = ttk.Label(frame, font=roboto_font_, text="Include Time?:")
        include_time_label.grid(row=2, column=0, sticky="w")
        include_time_options = ["Yes", "No"]
        include_time_combobox = ttk.Combobox(frame, font=roboto_font_, values=include_time_options, state="readonly")
        include_time_combobox.current(include_time_options.index(hyperparameters["include_time"]))
        include_time_combobox.grid(row=2, column=1, padx=(10, 0), sticky="w")

        # Maximum tokens
        max_tokens_label = ttk.Label(frame, font=roboto_font_, text="Max response Tokens:")
        max_tokens_label.grid(row=3, column=0, sticky="w")
        max_tokens_entry = ttk.Entry(frame, font=roboto_font_, )
        max_tokens_entry.insert(0, hyperparameters["max_tokens"])
        max_tokens_entry.grid(row=3, column=1, padx=(10, 0), sticky="w")

        # Messages in memory
        messages_in_memory_label = ttk.Label(frame, font=roboto_font_, text="Messages in memory:")
        messages_in_memory_label.grid(row=4, column=0, sticky="w")
        messages_in_memory_entry = ttk.Entry(frame, font=roboto_font_)
        messages_in_memory_entry.insert(0, hyperparameters["messages_in_memory"])
        messages_in_memory_entry.grid(row=4, column=1, padx=(10, 0), sticky="w")

        # Temperature
        temperature_label = ttk.Label(frame, font=roboto_font_, text="Temperature:")
        temperature_label.grid(row=5, column=0, sticky="w")
        temperature_entry = ttk.Entry(frame, font=roboto_font_)
        temperature_entry.insert(0, hyperparameters["temperature"])
        temperature_entry.grid(row=5, column=1, padx=(10, 0), sticky="w")

        # System message
        system_message_label = ttk.Label(frame, font=roboto_font_, text="System message:")
        system_message_label.grid(row=6, column=0, sticky="w")
        system_message_text: tk.Text = tk.Text(frame, font=roboto_font_, height=1)
        system_message_text.insert("1.0", hyperparameters["system_message"][:-1])
        system_message_text.grid(row=6, column=1, padx=(10, 0), sticky="news")

        # OpenAI api key
        openai_api_key_label = ttk.Label(frame, font=roboto_font_, text="OpenAI API key")
        openai_api_key_label.grid(row=9, column=0, sticky="w")
        openai_api_key_entry = tk.Entry(frame, font=roboto_font_)
        openai_api_key_entry.insert(0, hyperparameters["openai_api_key"])
        openai_api_key_entry.grid(row=9, column=1, padx=(10, 0), sticky="news")

        # Path to OAuth credentials
        path_to_OAuth_credentials_label = ttk.Label(frame, font=roboto_font_, text="Path to OAuth credentials:")
        path_to_OAuth_credentials_label.grid(row=10, column=0, sticky="w")
        path_to_OAuth_credentials_entry: tk.Entry = tk.Entry(frame, font=roboto_font_)
        path_to_OAuth_credentials_entry.insert(0, hyperparameters["path_to_OAuth_credentials"])
        path_to_OAuth_credentials_entry.grid(row=10, column=1, padx=(10, 0), sticky="news")

        # OAuth credentials token save location
        OAuth_credentials_token_save_location_label = ttk.Label(frame, font=roboto_font_,
                                                                text="OAuth credentials token save location:")
        OAuth_credentials_token_save_location_label.grid(row=11, column=0, sticky="w")
        OAuth_credentials_token_save_location_entry: tk.Entry = tk.Entry(frame, font=roboto_font_)
        OAuth_credentials_token_save_location_entry.insert(0, hyperparameters["OAuth_credentials_token_save_location"])
        OAuth_credentials_token_save_location_entry.grid(row=11, column=1, padx=(10, 0), sticky="news")

        # Save button
        save_button = ttk.Button(frame, text="Save", command=save_hyperparameters)
        save_button.grid(row=12, column=0, columnspan=2, pady=(20, 0))

        # Configure row and column weight to make text boxes expand
        frame.grid_rowconfigure(11, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Protocol when the window is closed
        root_.protocol("WM_DELETE_WINDOW", on_closing)

        root_.mainloop()


    def send_message(event: tk.Event = None) -> None:
        # 8 is when the the enter key is being pressed
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

            messages.append({'role': 'user',
                             'content': message + f"\n Time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"})

            # Display "Loading..." message
            loading_message = display_message("Bot: Loading...")

            # Get bot response in a separate thread
            threading.Thread(target=bot_response, args=(loading_message, messages)).start()

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


    def remove_message(text_widget: tk.Text) -> None:
        text_widget.configure(state='normal')  # Enable editing
        text_widget.delete('end-2l', 'end')  # Delete the second-to-last line
        text_widget.configure(state='disabled')  # Disable editing


    def delete_word(event):
        # Get the current cursor position
        cursor_position = input_text.index(tk.INSERT)

        if event.keysym == "BackSpace":
            # Delete the word before the cursor
            input_text.delete("insert-1c wordstart", cursor_position)
        elif event.keysym == "Delete":
            # Delete the word before the cursor
            input_text.delete(cursor_position, "insert-1c wordend")


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
