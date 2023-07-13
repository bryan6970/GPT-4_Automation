

string ="""
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
                              highlightbackground="#1C1C1C",
                              insertbackground="#FFFFFF",
                              height=2)
input_text.bind("<FocusIn>", set_border_color)  # Set border color on focus
input_text.bind("<FocusOut>", unset_border_color)  # Unset border color when focus is lost
input_text.bind("<Return>", send_message)  # Send message on Enter key
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
"""

string = string.replace("\n", ";")

print(string)