import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            txt_log.insert(tk.END, message + "\n")
        except OSError:
            break

def send_message(event=None):
    message = entry.get()
    if message:
        try:
            client_socket.sendall(message.encode())
            entry.delete(0, tk.END)
        except OSError:
            messagebox.showerror("Error", "Failed to send message to the server")

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        client_socket.close()
        root.destroy()

def connect_to_server():
    global client_socket
    host = '192.168.0.6'
    port = 65432

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        messagebox.showerror("Error", "The server is not available.")
        return

    username = entry_username.get()
    if username:
        client_socket.sendall(username.encode())
        waiting = client_socket.recv(1024).decode()
        txt_log.insert(tk.END, waiting + "\n")
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()
        btn_connect.config(state=tk.DISABLED)
        entry_username.config(state=tk.DISABLED)
        entry.focus_set()
    else:
        messagebox.showwarning("Warning", "Please enter a username.")

root = tk.Tk()
root.title("Quiz Game Client")

# Setting a background color for the application
root.configure(bg="#ECECEC")  # Light gray background

# Apply some styling to the frames
frame = tk.Frame(root, bg="#ECECEC")  # Light gray background
frame.pack()

# Apply styling to the text widget (adjusting font family and size)
txt_log = scrolledtext.ScrolledText(frame, height=15, width=50, bg="white", fg="black", font=("Arial", 12))  # White background, black text, font size 12
txt_log.pack(padx=10, pady=10)

# Apply some styling to the entry widget (adjusting font family and size)
entry = tk.Entry(frame, width=40, bg="#FFFFFF", fg="#333333", font=("Arial", 11))  # White background, dark gray text, font size 11
entry.pack(side=tk.LEFT, padx=5, pady=5)
entry.bind("<Return>", send_message)

# Apply styling to the send button
btn_send = tk.Button(frame, text="Send", command=send_message, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))  # Green button, bold font
btn_send.pack(side=tk.LEFT, padx=5, pady=5)

frame_username = tk.Frame(root, bg="#ECECEC")  # Light gray background
frame_username.pack()

# Apply styling to the label and entry for username (adjusting font family and size)
label_username = tk.Label(frame_username, text="Enter Username:", bg="#ECECEC", font=("Arial", 11))  # Light gray background, font size 11
label_username.pack(side=tk.LEFT, padx=5, pady=5)

entry_username = tk.Entry(frame_username, width=20, bg="#FFFFFF", fg="#333333", font=("Arial", 11))  # White background, dark gray text, font size 11
entry_username.pack(side=tk.LEFT, padx=5, pady=5)

# Apply styling to the connect button
btn_connect = tk.Button(frame_username, text="Connect", command=connect_to_server, bg="#2196F3", fg="white", font=("Arial", 11))  # Blue button, font size 11
btn_connect.pack(side=tk.LEFT, padx=5, pady=5)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
