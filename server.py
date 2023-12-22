import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import time

host = '192.168.0.6'
port = 65432
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

questions_and_answers = [
    ("What is the capital of France?", "Paris"),
    ("What is 3 times 3?", "9"),
    ("What is the name of our galaxy?", "Milky Way")
]

# GUI setup
root = tk.Tk()
root.title("Quiz Game Server")

frame = tk.Frame(root)
frame.pack()

txt_clients = scrolledtext.ScrolledText(frame, height=10, width=100)
txt_clients.pack()
txt_clients.insert(tk.END, "Connected Clients:\n")
txt_clients.config(state=tk.DISABLED)

txt_log = scrolledtext.ScrolledText(frame, height=10, width=100)
txt_log.pack()
txt_log.insert(tk.END, "Game Log:\n")
txt_log.config(state=tk.DISABLED)

# Synchronization variables
max_players = 2
connected_players = 0
players_ready = threading.Event()

# Function to update GUI text
def update_text(widget, text):
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, text + "\n")
    widget.config(state=tk.DISABLED)

# Client handler function
def handle_client(conn, addr):
    global connected_players

    update_text(txt_log, f"New connection from {addr}")

    username = conn.recv(1024).decode().strip()
    conn.sendall("Waiting for players to join...".encode())

    update_text(txt_clients, f"User connected with username: {username}")

    # Wait for other players to connect
    with threading.Lock():
        connected_players += 1
        update_text(txt_log, f"Player {username} connected. {connected_players}/{max_players} players connected.")
        if connected_players == max_players:
            players_ready.set()
            conn.sendall("All players are here ! \n The quiz starts now! \n You have 10 seconds to answer for each question!".encode())

    # Wait for all players to be ready
    players_ready.wait()

    score = 0  # Initialize

    # Send questions to the client
    for question, correct_answer in questions_and_answers:
        conn.sendall(question.encode())
        client_answer = ""
        
        #Starting the timer
        start_time = time.time()
        duration = 10
        
        client_answer = conn.recv(1024).decode().lower()

        if time.time() - start_time > duration:
            conn.sendall(f"Time Limit Exceeded! \n The answer was: {correct_answer}".encode())
            update_text(txt_log, f"{username} answered with time limit excess.")
        elif client_answer != "" and client_answer == correct_answer.lower():
            answer_score = int((time.time() - start_time)*50)
            score += answer_score
            conn.sendall(f"Correct! \n +{answer_score} points.".encode())
            update_text(txt_log, f"{username} answered correctly.")
        elif client_answer != correct_answer.lower():
            conn.sendall("Incorrect!".encode())
            update_text(txt_log, f"{username} answered incorrectly.")

    # Send the final score to the client
    conn.sendall(f"Your final score is {score}".encode())
    conn.close()

    # Update the client list and log
    with threading.Lock():
        update_text(txt_clients, f"{username} finished with a score of {score}")
        update_text(txt_log, f"{username} disconnected.")

# Main server loop
def start_server():
    update_text(txt_log, "Server is running and waiting for connections...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        update_text(txt_log, f"Active connections: {threading.activeCount() - 1}")

# Run the server in a separate thread so that it doesn’t block the GUI
threading.Thread(target=start_server).start()

root.mainloop()
