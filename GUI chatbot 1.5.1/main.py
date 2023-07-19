from tkinter import scrolledtext
from PIL import ImageTk, Image
import threading
import logging
import Bot
import tkinter as tk
from tkinter import ttk
import json
from tkinter.font import Font

# Configure logging level
logging.basicConfig(filename="logs.log", level=logging.DEBUG)

PATH_TO_IMAGE: str = r"../Images/GPT.png"

with open("hyperparameters.json", "r") as file:
    hyperparameters = json.load(file)

print(hyperparameters)

spliter = "g1404018thaaou"


def bot_response(loading_message: tk.Text, chat_history) -> None:
    # Get bot response
    chat_history = chat_history[-hyperparameters["messages_in_memory"]:]

    logging.debug(f"{hyperparameters['chat_selection']} is being used")

    if hyperparameters["chat_selection"] == "Chat with function calls":
        bot_reply = Bot.run_convo_with_function_calls(chat_history, hyperparameters["model"],
                                                      hyperparameters["max_tokens"],
                                                      hyperparameters["temperature"],
                                                      hyperparameters["use_python"])
    elif hyperparameters["chat_selection"] == "function calls with explanation":
        bot_reply = Bot.run_convo_with_function_calls_and_explanation(chat_history, hyperparameters["model"],
                                                                      hyperparameters["max_tokens"],
                                                                      hyperparameters["temperature"],
                                                                      hyperparameters["use_python"])
    else:
        bot_reply = Bot.run_convo_pure_chat(chat_history, hyperparameters["model"], hyperparameters["max_tokens"],
                                            hyperparameters["temperature"])

    # bot_reply = "api not enageged"

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
        chat_selection: str = chat_selection_combobox.get()
        use_python: str = use_python_combobox.get()
        max_tokens: int = int(max_tokens_entry.get())
        messages_in_memory: int = int(messages_in_memory_entry.get())
        temperature: float = float(temperature_entry.get())
        pre_text: str = pre_text_text.get("1.0", tk.END)
        post_text: str = post_text_text.get("1.0", tk.END)
        system_message: str = system_message_text.get("1.0", tk.END)

        # Save the hyperparameters
        hyperparameters = {
            "model": selected_model,
            "chat_selection": chat_selection,
            "use_python": use_python,
            "max_tokens": max_tokens,
            "messages_in_memory": messages_in_memory,
            "temperature": temperature,
            "pre_text": pre_text,
            "post_text": post_text,
            "system_message": system_message,
            "saved": True
        }

        with open("hyperparameters.json", "w") as f:
            json.dump(hyperparameters, f)

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

    roboto_font_ = Font(family="Roboto", size=15)

    # Create a frame to hold the hyperparameters
    frame = ttk.Frame(root_, padding=20)
    frame.pack()

    # Model selection
    model_label = ttk.Label(frame, font=roboto_font_, text="Model:")
    model_label.grid(row=0, column=0, sticky="w")
    models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]
    model_combobox = ttk.Combobox(frame, font=roboto_font_, values=models, state="readonly")
    model_combobox.current(models.index(hyperparameters["model"]))
    model_combobox.bind("<<ComboboxSelected>>", set_appropriate_max_token)
    model_combobox.grid(row=0, column=1, padx=(10, 0), sticky="w")

    # Chat selection
    chat_selection_label = ttk.Label(frame, font=roboto_font_, text="Chat type:")
    chat_selection_label.grid(row=1, column=0, sticky="w")
    chat_selections = ["Pure chat", "Chat with function calls", "function calls with explanation"]
    chat_selection_combobox = ttk.Combobox(frame, font=roboto_font_, values=chat_selections, state="readonly")
    chat_selection_combobox.current(chat_selections.index(hyperparameters["chat_selection"]))
    chat_selection_combobox.grid(row=1, column=1, padx=(10, 0), sticky="w")

    # Use python
    use_python_label = ttk.Label(frame, font=roboto_font_, text="Use python?:")
    use_python_label.grid(row=2, column=0, sticky="w")
    use_python_options = ["Yes", "No"]
    use_python_combobox = ttk.Combobox(frame, font=roboto_font_, values=use_python_options, state="readonly")
    use_python_combobox.current(use_python_options.index(hyperparameters["use_python"]))
    use_python_combobox.grid(row=2, column=1, padx=(10, 0), sticky="w")

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

    # Pre text
    pre_text_label = ttk.Label(frame, font=roboto_font_, text="Pre-text:")
    pre_text_label.grid(row=6, column=0, sticky="w")
    pre_text_text: tk.Text = tk.Text(frame, font=roboto_font_, height=1)
    pre_text_text.insert("1.0", hyperparameters["pre_text"][:-1])
    pre_text_text.grid(row=6, column=1, padx=(10, 0), sticky="news")

    # Post text
    post_text_label = ttk.Label(frame, font=roboto_font_, text="Post-text:")
    post_text_label.grid(row=7, column=0, sticky="w")
    post_text_text: tk.Text = tk.Text(frame, font=roboto_font_, height=1)
    post_text_text.insert("1.0", hyperparameters["post_text"][:-1])
    post_text_text.grid(row=7, column=1, padx=(10, 0), sticky="news")

    # System message
    system_message_label = ttk.Label(frame, font=roboto_font_, text="System message:")
    system_message_label.grid(row=8, column=0, sticky="w")
    system_message_text: tk.Text = tk.Text(frame, font=roboto_font_, height=1)
    system_message_text.insert("1.0", hyperparameters["system_message"][:-1])
    system_message_text.grid(row=8, column=1, padx=(10, 0), sticky="news")

    # Save button
    save_button = ttk.Button(frame, text="Save", command=save_hyperparameters)
    save_button.grid(row=9, column=0, columnspan=2, pady=(20, 0))

    # Configure row and column weight to make text boxes expand
    frame.grid_rowconfigure(11, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    # Protocol when the window is closed
    root_.protocol("WM_DELETE_WINDOW", on_closing)

    root_.mainloop()


def send_message(event: tk.Event = None) -> None:
    # 8 is when the enter key is being pressed
    if event.state != 8:
        return None

    message: str = input_text.get("1.0", tk.END).strip()
    if message:
        # Display the user message in the chat area
        display_message(f"You: {message}")

        # Format it into the right format. Using .split function to separate messages
        chat_history = chat_area.get("1.0", tk.END).strip().replace("Bot:", spliter + "Bot:").replace("System:",
                                                                                                      spliter + "System:").replace(
            "You:", spliter + "You:")

        chat_history = chat_history.split(spliter)

        chat_history_ = [{"role": "system",
                          "content": hyperparameters["system_message"]}]

        for message in chat_history:
            if message[:3] == "Bot":
                chat_history_.append({"role": "assistant", "content": message[5:]})
            elif message[:3] == "You":
                chat_history_.append({"role": "user",
                                      "content": hyperparameters["pre_text"] + message[5:] + hyperparameters[
                                          "post_text"]})

        print(chat_history_)

        # Display "Loading..." message
        loading_message = display_message("Bot: Loading...")

        # Get bot response in a separate thread
        threading.Thread(target=bot_response, args=(loading_message, chat_history_)).start()

        input_text.delete("1.0", tk.END)  # Clear the input text


def set_border_color(event: tk.Event) -> None:
    input_text.config(highlightbackground="#282828")


def unset_border_color(event: tk.Event) -> None:
    input_text.config(highlightbackground="#1C1C1C")


def display_message(message: str) -> tk.Text:
    chat_area.configure(state='normal')  # Enable editing
    chat_area.insert(tk.END, message + "\n")
    chat_area.see(tk.END)  # Auto scroll to the latest message
    chat_area.configure(state='disabled')  # Disable editing

    return chat_area


def remove_message(text_widget: tk.Text) -> None:
    text_widget.configure(state='normal')  # Enable editing
    text_widget.delete('end-2l', 'end')  # Delete the second-to-last line
    text_widget.configure(state='disabled')  # Disable editing


# Create the main window
root: tk.Tk = tk.Tk()
root.title("Chat App")
root.configure(background="#1C1C1C")

roboto_font = Font(family="Roboto", size=10)
segoe_UI_font = Font(family="Segoe UI", size=10)

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
input_text.bind("<Key>", lambda event: input_text.configure(
    height=int(input_text.index('end-1c').split('.')[0])))  # Make the textbox size increase with input
input_text.bind("<Return>", lambda event: input_text.configure(
    height=int(input_text.index('end-1c').split('.')[0])))  # Make the textbox size increase with input

input_text.grid(row=0, column=0, sticky="ew")

input_text.bind("<FocusIn>", set_border_color)  # Set border color on focus
input_text.bind("<FocusOut>", unset_border_color)  # Unset border color when focus is lost
input_text.bind("<Return>", send_message)  # Send message on Enter key

# Change the color of the text indicator to white
input_text.configure(insertbackground="#FFFFFF", highlightthickness=0)
input_text.grid(row=0, column=0, sticky="ew")

# Create a send button
send_button: tk.Button = tk.Button(input_frame, font=roboto_font, text="Send", command=send_message)
send_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

# Configure column weight to make it scale with window size
input_frame.grid_columnconfigure(0, weight=1)

# Create the "hyper params" button
hyper_button: tk.Button = tk.Button(root, font=roboto_font, text="Edit hyperparameters",
                                    command=open_hyperparameters_window,
                                    bg="#282828",
                                    fg="#FFFFFF", activebackground="#1C1C1C", activeforeground="#FFFFFF")
hyper_button.place(relx=1, rely=0, anchor="ne", x=-10, y=10)

# Configure the chat frame to scale when window is resized
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

root.mainloop()
