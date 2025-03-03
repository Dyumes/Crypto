from tkinter import *
from connection import *
from threading import *

connect()

window = Tk()
window.title("ChatApp")
window.geometry("434x644")

chat_area = Text(window, height=20, width=50, wrap=WORD)
entry_field = Entry(window, width=40)
send_button = Button(window, text=">")

# Grid management
chat_area.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
entry_field.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
send_button.grid(row=1, column=1, padx=10, pady=10)
window.grid_rowconfigure(0, weight=1)  # Allow the chat area to expand
window.grid_rowconfigure(1, weight=0)  # Don't allow the entry/button area to expand
window.grid_columnconfigure(0, weight=1)  # Allow the entry field to expand horizontally

# Action configs
def send_message():
    msg = entry_field.get()
    chat_area.config(state=NORMAL)
    chat_area.insert(END, f"\n<You> {msg}")
    chat_area.see(END)
    chat_area.config(state=DISABLED)
    entry_field.delete(0, END)
    send(msg)

def receive_message():
    while True:
        (type, msg) = listen()
        if msg!=None:
            chat_area.config(state=NORMAL)
            chat_area.insert(END, f"\n<User> {msg.encode('latin1')}")
            chat_area.see(END)
            chat_area.config(state=DISABLED)

def key_handler(event):
    if event.keycode == 13:
        send_message()

window.bind("<Key>", key_handler)
send_button.config(command=send_message)
listening = Thread(target=receive_message)
listening.start()

window.mainloop()