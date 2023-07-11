import tkinter as tk
from tkinter import scrolledtext
from PIL import ImageTk, Image
import threading
import subprocess
import json
import logging
import Bot

# Configure logging level
logging.basicConfig(filename="logs.log", level=logging.DEBUG)

PATH_TO_IMAGE: str = r"../Images/GPT.png"

with open("hyperparameters.json", "r") as file:
    hyperparameters = json.load(file)

print(hyperparameters)


def bot_response(loading_message: tk.Text, chat_history) -> None:
    # Get bot response
    chat_history = chat_history[-hyperparameters["messages_in_memory"]:]

    logging.debug(f"{hyperparameters['chat_selection']} is being used")

    if hyperparameters["chat_selection"] == "Chat with function calls":
        bot_reply = Bot.run_convo_with_function_calls(chat_history, hyperparameters["model"],
                                                      hyperparameters["max_tokens"],
                                                      hyperparameters["temperature"])
    elif hyperparameters["chat_selection"] == "function calls with explanation":
        bot_reply = Bot.run_convo_with_function_calls_and_explanation(chat_history, hyperparameters["model"],
                                                                      hyperparameters["max_tokens"],
                                                                      hyperparameters["temperature"])
    else:
        bot_reply = Bot.run_convo_pure_chat(chat_history, hyperparameters["model"], hyperparameters["max_tokens"],
                                            hyperparameters["temperature"])

    # Remove the "Loading..." message
    remove_message(loading_message)

    # Display the bot response in the chat area
    display_message(f"\nBot: {bot_reply}")


def open_hyperparameters_window() -> None:
    # Convert the hyperparameters to a string representation
    hyperparameters_string = "||".join([f"{key}={value}" for key, value in hyperparameters.items()])

    # Run the subprocess and capture the output

    details = subprocess.Popen(['python', 'hyper_params.py'] + hyperparameters_string.split("||"),
                               stdout=subprocess.PIPE)

    with open("hyperparameters.json", "r") as file:
        load_hyperparameters(json.load(file))

    # Old format
    # output, _ = details.communicate()
    #
    # output = output.decode()
    # output = output.replace("\'", "\"")
    #
    # logging.debug(output)
    #
    # load_hyperparameters(json.loads(output))


def load_hyperparameters(output: dict) -> None:
    global hyperparameters
    hyperparameters = output


def send_message(event: tk.Event = None) -> None:
    message: str = input_text.get("1.0", tk.END).strip()
    if message:
        # Display the user message in the chat area
        display_message(f"You: {message}")

        # Get chat history
        chat_history = chat_area.get("1.0", tk.END).strip().split("\n")

        chat_history_ = [{"role": "system",
                          "content": hyperparameters["system_message"]}]

        for message in chat_history:
            if message[:3] == "Bot":
                chat_history_.append({"role": "assistant", "content": message[5:]})
            elif message[:3] == "You":
                chat_history_.append({"role": "user",
                                      "content": hyperparameters["pre_text"] + message[5:] + hyperparameters[
                                          "post_text"]})

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

# Set the window logo
logo_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(PATH_TO_IMAGE))
root.iconphoto(True, logo_image)

# Create a frame to hold the chat area
chat_frame: tk.Frame = tk.Frame(root, bg="#1C1C1C")
chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Create a scrolled text widget for the chat area
chat_area: scrolledtext.ScrolledText = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, bg="#1C1C1C", fg="#EFEFEF",
                                                                 width=50,
                                                                 height=20)

chat_area.configure(state='disabled')  # Make the chat area read-only
chat_area.pack(fill="both", expand=True)

# Create a frame to hold the input text and send button
input_frame: tk.Frame = tk.Frame(root, bg="#282828")
input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

# Create an input text widget
input_text: tk.Text = tk.Text(input_frame, wrap=tk.WORD, bg="#282828", fg="#FFFFFF", highlightbackground="#1C1C1C",
                              insertbackground="#FFFFFF",
                              height=2)
input_text.bind("<FocusIn>", set_border_color)  # Set border color on focus
input_text.bind("<FocusOut>", unset_border_color)  # Unset border color when focus is lost
input_text.bind("<Return>", send_message)  # Send message on Enter key
input_text.grid(row=0, column=0, sticky="ew")

# Create a send button
send_button: tk.Button = tk.Button(input_frame, text="Send", command=send_message)
send_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

# Configure column weight to make it scale with window size
input_frame.grid_columnconfigure(0, weight=1)

# Create the "hyper params" button
hyper_button: tk.Button = tk.Button(root, text="Edit hyperparameters", command=open_hyperparameters_window,
                                    bg="#282828",
                                    fg="#FFFFFF", activebackground="#1C1C1C", activeforeground="#FFFFFF")
hyper_button.place(relx=1, rely=0, anchor="ne", x=-10, y=10)

# Configure the chat frame to scale when window is resized
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

root.mainloop()
