import os.path

import pyforest
import tkinter as tk
from tkinter import scrolledtext
from PIL import ImageTk, Image

import repository_utils

PATH_TO_IMAGE: str = os.path.join(repository_utils.get_repo_dir(), r"Images\GPT.png")


def send_message(event: tk.Event = None) -> None:
    message: str = input_text.get("1.0", tk.END).strip()
    if message:
        # Display the user message in the chat area
        display_message(f"You: {message}")

        # Get bot response
        bot_reply: str = bot_response(message)

        # Display the bot response in the chat area
        display_message(f"Bot: {bot_reply}")

        input_text.delete("1.0", tk.END)  # Clear the input text


def set_border_color(event: tk.Event) -> None:
    input_text.config(highlightbackground="#282828")


def unset_border_color(event: tk.Event) -> None:
    input_text.config(highlightbackground="#1C1C1C")


def display_message(message: str) -> None:
    chat_area.configure(state='normal')  # Enable editing
    chat_area.insert(tk.END, message + "\n")
    chat_area.see(tk.END)  # Auto scroll to the latest message
    chat_area.configure(state='disabled')  # Disable editing


def bot_response(user_message: str) -> str:
    # Add your bot response logic here
    # Return the bot response as a string
    return "Hello, I am a chatbot"


# Create the main window
window: tk.Tk = tk.Tk()
window.title("Chat App")
window.configure(background="#1C1C1C")

# Set the window logo
logo_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(PATH_TO_IMAGE))
window.iconphoto(True, logo_image)

# Create a frame to hold the chat area
chat_frame: tk.Frame = tk.Frame(window, bg="#1C1C1C")
chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Create a scrolled text widget for the chat area
chat_area: scrolledtext.ScrolledText = scrolledtext.ScrolledText(chat_frame, bg="#1C1C1C", fg="#EFEFEF", width=50,
                                                                 height=20)
chat_area.configure(state='disabled')  # Make the chat area read-only
chat_area.pack(fill="both", expand=True)

# Create a frame to hold the input text and send button
input_frame: tk.Frame = tk.Frame(window, bg="#282828")
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

# Configure the chat frame to scale when window is resized
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)

window.mainloop()

repository_utils.auto_import(pyforest.active_imports(), __file__)


window.mainloop()

repository_utils.auto_import(pyforest.active_imports(), __file__)
