import sys
import tkinter as tk
from tkinter import ttk
import json
import signal


def save_hyperparameters() -> None:
    # Get selected hyperparameters from the UI
    selected_model = model_combobox.get()
    max_tokens = int(max_tokens_entry.get())
    temperature = float(temperature_entry.get())

    # Save the hyperparameters to a file
    hyperparameters = {
        "model": selected_model,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    with open("hyperparameters.json", "w") as file:
        json.dump(hyperparameters, file)

    print("Hyperparameters saved!")

    # Create a signal file to indicate new hyperparameters
    with open("hyperparameters.signal", "w") as signal_file:
        signal_file.write("")

    # Terminate the process
    sys.exit()


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
model_combobox.current(0)
model_combobox.grid(row=0, column=1, padx=(10, 0), sticky="w")

# Maximum tokens
max_tokens_label = ttk.Label(frame, text="Max Tokens:")
max_tokens_label.grid(row=1, column=0, sticky="w")
max_tokens_entry = ttk.Entry(frame)
max_tokens_entry.insert(0, "1024")
max_tokens_entry.grid(row=1, column=1, padx=(10, 0), sticky="w")

# Temperature
temperature_label = ttk.Label(frame, text="Temperature:")
temperature_label.grid(row=2, column=0, sticky="w")
temperature_entry = ttk.Entry(frame)
temperature_entry.insert(0, "1")
temperature_entry.grid(row=2, column=1, padx=(10, 0), sticky="w")

# Save button
save_button = ttk.Button(frame, text="Save", command=save_hyperparameters)
save_button.grid(row=3, column=0, columnspan=2, pady=(20, 0))

root.mainloop()
