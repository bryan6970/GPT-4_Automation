import sys
import tkinter as tk
from tkinter import ttk
import json
import signal

hyperparameters: dict = {}


def save_hyperparameters() -> None:
    global hyperparameters
    # Get selected hyperparameters from the UI
    selected_model: str = model_combobox.get()
    chat_selection: str = chat_selection_combobox.get()
    max_tokens: int = int(max_tokens_entry.get())
    messages_in_memory: int = int(messages_in_memory_entry.get())
    temperature: float = float(temperature_entry.get())
    pre_text: str = pre_text_text.get("1.0", tk.END)
    post_text: str = post_text_text.get("1.0", tk.END)

    # Save the hyperparameters
    hyperparameters["model"] = selected_model
    hyperparameters["chat_selection"] = chat_selection
    hyperparameters['max_tokens'] = max_tokens
    hyperparameters["messages_in_memory"] = messages_in_memory
    hyperparameters["temperature"] = temperature
    hyperparameters["pre_text"] = pre_text
    hyperparameters["post_text"] = post_text

    print("Hyperparameters saved!", file=sys.stderr)

    print(hyperparameters)

    with open("hyperparameters.json", "w") as f:
        json.dump(hyperparameters, f)

    # Terminate the process
    sys.exit()


def set_appropriate_max_token(event: tk.Event) -> None:
    # Delete old tokens
    max_tokens_entry.delete(0, tk.END)

    # Set max tokens based on the selected model
    if model_combobox.get() == "gpt-3.5-16k":
        max_tokens_entry.insert(0, "16000")
    elif model_combobox.get() == "gpt-4":
        max_tokens_entry.insert(0, "8000")
    elif model_combobox.get() == "gpt-3.5-turbo":
        max_tokens_entry.insert(0, "4000")
    else:
        max_tokens_entry.insert(0, hyperparameters["max_tokens"])


# load hyperparams
for argument in sys.argv[1:]:
    print(argument, file=sys.stderr)
    key, value = argument.split("=")
    hyperparameters[key] = value

# Create the hyperparameters window
root = tk.Tk()
root.title("Hyperparameters")
root.configure(background="#1C1C1C")

# Create a frame to hold the hyperparameters
frame = ttk.Frame(root, padding=20)
frame.pack()

# Model selection
model_label = ttk.Label(frame, text="Model:")
model_label.grid(row=0, column=0, sticky="w")
models = ["gpt-3.5-turbo", "gpt-3.5-16k", "gpt-4"]
model_combobox = ttk.Combobox(frame, values=models, state="readonly")
model_combobox.current(models.index(hyperparameters["model"]))
model_combobox.bind("<<ComboboxSelected>>", set_appropriate_max_token)
model_combobox.grid(row=0, column=1, padx=(10, 0), sticky="w")


# Chat selection
chat_selection_label = ttk.Label(frame, text="Chat type:")
chat_selection_label.grid(row=1, column=0, sticky="w")
chat_selections = ["Pure chat", "Chat with function calls"]
chat_selection_combobox = ttk.Combobox(frame, values=chat_selections, state="readonly")
chat_selection_combobox.current(chat_selections.index(hyperparameters["chat_selection"]))
chat_selection_combobox.grid(row=1, column=1, padx=(10, 0), sticky="w")

# Maximum tokens
max_tokens_label = ttk.Label(frame, text="Max Tokens:")
max_tokens_label.grid(row=2, column=0, sticky="w")
max_tokens_entry = ttk.Entry(frame)
max_tokens_entry.insert(0, hyperparameters["max_tokens"])
max_tokens_entry.grid(row=2, column=1, padx=(10, 0), sticky="w")

# Messages in memory
messages_in_memory_label = ttk.Label(frame, text="Messages in memory:")
messages_in_memory_label.grid(row=3, column=0, sticky="w")
messages_in_memory_entry = ttk.Entry(frame)
messages_in_memory_entry.insert(0, hyperparameters["messages_in_memory"])
messages_in_memory_entry.grid(row=3, column=1, padx=(10, 0), sticky="w")

# Temperature
temperature_label = ttk.Label(frame, text="Temperature:")
temperature_label.grid(row=4, column=0, sticky="w")
temperature_entry = ttk.Entry(frame)
temperature_entry.insert(0, hyperparameters["temperature"])
temperature_entry.grid(row=4, column=1, padx=(10, 0), sticky="w")

# Pre text
pre_text_label = ttk.Label(frame, text="Pre-text:")
pre_text_label.grid(row=5, column=0, sticky="w")
pre_text_text: tk.Text = tk.Text(frame, height=1)
pre_text_text.insert("1.0", hyperparameters["pre_text"][:-1])
pre_text_text.grid(row=5, column=1, padx=(10, 0), sticky="w")

# Post text
post_text_label = ttk.Label(frame, text="Post-text:")
post_text_label.grid(row=6, column=0, sticky="w")
post_text_text: tk.Text = tk.Text(frame, height=1)
post_text_text.insert("1.0", hyperparameters["post_text"][-1])
post_text_text.grid(row=6, column=1, padx=(10, 0), sticky="w")

# Save button
save_button = ttk.Button(frame, text="Save", command=save_hyperparameters)
save_button.grid(row=7, column=0, columnspan=2, pady=(20, 0))

root.mainloop()
