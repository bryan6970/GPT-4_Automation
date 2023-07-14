import sys
import tkinter as tk
from tkinter import ttk
import json
from tkinter import Tk, Label, Entry
from tkinter.font import Font


def save_hyperparameters() -> None:
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

    print(f"Hyperparameters saved! \n {hyperparameters}", file=sys.stderr)

    with open("hyperparameters.json", "w") as f:
        json.dump(hyperparameters, f)

    # Terminate the process
    sys.exit()


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


# load hyperparams
with open("hyperparameters.json", "r") as f:
    hyperparameters = json.load(f)

# Create the hyperparameters window
root = tk.Tk()
root.title("Hyperparameters")
root.configure(background="#1C1C1C")

roboto_font = Font(family="Roboto", size=10)

# Create a frame to hold the hyperparameters
frame = ttk.Frame(root, padding=20)
frame.pack()

# Model selection
model_label = ttk.Label(frame, font=roboto_font, text="Model:")
model_label.grid(row=0, column=0, sticky="w")
models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]
model_combobox = ttk.Combobox(frame, font=roboto_font, values=models, state="readonly")
model_combobox.current(models.index(hyperparameters["model"]))
model_combobox.bind("<<ComboboxSelected>>", set_appropriate_max_token)
model_combobox.grid(row=0, column=1, padx=(10, 0), sticky="w")

# Chat selection
chat_selection_label = ttk.Label(frame, font=roboto_font, text="Chat type:")
chat_selection_label.grid(row=1, column=0, sticky="w")
chat_selections = ["Pure chat", "Chat with function calls", "function calls with explanation"]
chat_selection_combobox = ttk.Combobox(frame, font=roboto_font, values=chat_selections, state="readonly")
chat_selection_combobox.current(chat_selections.index(hyperparameters["chat_selection"]))
chat_selection_combobox.grid(row=1, column=1, padx=(10, 0), sticky="w")

# Use python
use_python_label = ttk.Label(frame, font=roboto_font, text="Use python?:")
use_python_label.grid(row=2, column=0, sticky="w")
use_python_options = ["Yes", "No"]
use_python_combobox = ttk.Combobox(frame, font=roboto_font, values=use_python_options, state="readonly")
use_python_combobox.current(use_python_options.index(hyperparameters["use_python"]))
use_python_combobox.grid(row=2, column=1, padx=(10, 0), sticky="w")

# Maximum tokens
max_tokens_label = ttk.Label(frame, font=roboto_font, text="Max response Tokens:")
max_tokens_label.grid(row=3, column=0, sticky="w")
max_tokens_entry = ttk.Entry(frame, font=roboto_font, )
max_tokens_entry.insert(0, hyperparameters["max_tokens"])
max_tokens_entry.grid(row=3, column=1, padx=(10, 0), sticky="w")

# Messages in memory
messages_in_memory_label = ttk.Label(frame, font=roboto_font, text="Messages in memory:")
messages_in_memory_label.grid(row=4, column=0, sticky="w")
messages_in_memory_entry = ttk.Entry(frame, font=roboto_font)
messages_in_memory_entry.insert(0, hyperparameters["messages_in_memory"])
messages_in_memory_entry.grid(row=4, column=1, padx=(10, 0), sticky="w")

# Temperature
temperature_label = ttk.Label(frame, font=roboto_font, text="Temperature:")
temperature_label.grid(row=5, column=0, sticky="w")
temperature_entry = ttk.Entry(frame, font=roboto_font)
temperature_entry.insert(0, hyperparameters["temperature"])
temperature_entry.grid(row=5, column=1, padx=(10, 0), sticky="w")

# Pre text
pre_text_label = ttk.Label(frame, font=roboto_font, text="Pre-text:")
pre_text_label.grid(row=6, column=0, sticky="w")
pre_text_text: tk.Text = tk.Text(frame, font=roboto_font, height=1)
pre_text_text.insert("1.0", hyperparameters["pre_text"][:-1])
pre_text_text.grid(row=6, column=1, padx=(10, 0), sticky="news")

# Post text
post_text_label = ttk.Label(frame, font=roboto_font, text="Post-text:")
post_text_label.grid(row=7, column=0, sticky="w")
post_text_text: tk.Text = tk.Text(frame, font=roboto_font, height=1)
post_text_text.insert("1.0", hyperparameters["post_text"][:-1])
post_text_text.grid(row=7, column=1, padx=(10, 0), sticky="news")

# System message
system_message_label = ttk.Label(frame, font=roboto_font, text="System message:")
system_message_label.grid(row=8, column=0, sticky="w")
system_message_text: tk.Text = tk.Text(frame, font=roboto_font, height=1)
system_message_text.insert("1.0", hyperparameters["system_message"][:-1])
system_message_text.grid(row=8, column=1, padx=(10, 0), sticky="news")

# Save button
save_button = ttk.Button(frame, text="Save", command=save_hyperparameters)
save_button.grid(row=9, column=0, columnspan=2, pady=(20, 0))

# Configure row and column weight to make text boxes expand
frame.grid_rowconfigure(11, weight=1)
frame.grid_columnconfigure(1, weight=1)

root.mainloop()


print('hi')
