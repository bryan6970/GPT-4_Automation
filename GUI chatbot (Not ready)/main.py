import os.path
import time

import pyforest
import tkinter as tk
from tkinter import scrolledtext
from PIL import ImageTk, Image
import threading
import subprocess
import signal
import json

import repository_utils

PATH_TO_IMAGE: str = os.path.join(repository_utils.get_repo_dir(), r"Images\GPT.png")


def bot_response(message: str, loading_message: tk.Text) -> None:
    # Get bot response
    time.sleep(3)
    bot_reply = "hello"

    # Remove the "Loading..." message
    remove_message(loading_message)

    # Display the bot response in the chat area
    display_message(f"\nBot: {bot_reply}")


def open_hyperparameters_window() -> None:
    subprocess.Popen(['python', 'hyper_params.py'])


def load_hyperparameters() -> None:
    if os.path.exists("hyperparameters.signal"):
        with open("hyperparameters.json", "r") as file:
            hyperparameters = json.load(file)

        print(f"Hyperparameters loaded \nParameters:\n{hyperparameters}")

        # Process the loaded hyperparameters
        selected_model: str = hyperparameters["model"]
        max_tokens: int = hyperparameters["max_tokens"]
        temperature: float = hyperparameters["temperature"]

        # Perform further actions with the hyperparameters
        # ...

        # Remove the signal file
        os.remove("hyperparameters.signal")


def handle_signal(signum: int, frame) -> None:
    if signum == signal.SIGUSR1:
        load_hyperparameters()


def send_message(event: tk.Event = None) -> None:
    message: str = input_text.get("1.0", tk.END).strip()
    if message:
        # Display the user message in the chat area
        display_message(f"You: {message}")

        # Display "Loading..." message
        loading_message = display_message("Bot: Loading...")

        # Get bot response in a separate thread
        threading.Thread(target=bot_response, args=(message, loading_message)).start()

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

# Set the window logo
logo_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(PATH_TO_IMAGE))
root.iconphoto(True, logo_image)

# Create a frame to hold the chat area
chat_frame: tk.Frame = tk.Frame(root, bg="#1C1C1C")
chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Create a scrolled text widget for the chat area
chat_area: scrolledtext.ScrolledText = scrolledtext.ScrolledText(chat_frame, bg="#1C1C1C", fg="#EFEFEF", width=50,
                                                                 height=20)
chat_area.configure(state='disabled')  # Make the chat area read-only
chat_area.pack(fill="both", expand=True)

# Create a frame to hold the input text and send button
input_frame: tk.Frame = tk.Frame(root, bg="#282828")
input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

# Create an input text widget
input_text: tk.Text = tk.Text(input_frame, bg="#282828", fg="#FFFFFF", highlightbackground="#1C1C1C",
                              insertbackground="#FFFFFF",
                              height=2)
input_text.bind("<FocusIn>", set_border_color)  # Set border color on focus
input_text.bind("<FocusOut>", unset_border_color)  # Unset border color when focus is lost
input_text.bind("<Return>", send_message)  # Send message on Enter key
input_text.grid(row=0, column=0, sticky="ew")

# Create a send button
send_button: tk.Button = tk.Button(input_frame, text="Send", command=send_message)
send_button.grid(row=0, column=1, padx=(5, 0))

# Create the "hyper params" button
hyper_button: tk.Button = tk.Button(root, text="hyper params", command=open_hyperparameters_window, bg="#282828",
                                    fg="#FFFFFF", activebackground="#1C1C1C", activeforeground="#FFFFFF")
hyper_button.place(relx=1, rely=0, anchor="ne", x=-10, y=10)

# Configure the chat frame to scale when window is resized
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

root.mainloop()

repository_utils.auto_import(pyforest.active_imports(), __file__)
