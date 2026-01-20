import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = {}

def broadcast_user_list():
    """שולח את רשימת המשתמשים לכולם"""
    user_list = ",".join(clients.values())
    protocol_msg = f"USERS_LIST:{user_list}\n"
    for client_socket in clients:
        try: client_socket.send(protocol_msg.encode('utf-8'))
        except: pass

def broadcast_message(message, sender_socket=None):
    """שולח הודעה לכולם"""
    final_msg = message + "\n"
    for client_socket in clients:
        if client_socket != sender_socket:
            try: client_socket.send(final_msg.encode('utf-8'))
            except: pass

def send_private_message(target_name, message, sender_socket):
    """שולח הודעה לאדם ספציפי"""
    final_msg = message + "\n"
    for sock, name in clients.items():
        if name == target_name:
            try: sock.send(final_msg.encode('utf-8'))
            except: pass

def handle_client(client_socket):
    username = ""
    try:
        username = client_socket.recv(1024).decode('utf-8').strip()
        
        if username in clients.values():
            client_socket.send("Error: Username taken.\n".encode('utf-8'))
            client_socket.close()
            return

        clients[client_socket] = username
        print(f"[NEW] {username} connected.")
        
        broadcast_message(f"Server: {username} has joined the chat.")
        broadcast_user_list()

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message: break
            
            if ":" in message:
                target, content = message.split(":", 1)
                full_msg = f"{username}: {content}"
                
                if target.lower() == "all":
                    broadcast_message(full_msg, client_socket)
                else:
                    # --- כאן השינוי: הוספת סימן זיהוי להודעה פרטית ---
                    private_msg = f"(Private) {username}: {content}"
                    send_private_message(target, private_msg, client_socket)
                    # -------------------------------------------------
            else:
                broadcast_message(f"{username}: {message}", client_socket)

    except: pass
    finally:
        if client_socket in clients:
            del clients[client_socket]
            broadcast_message(f"Server: {username} has left the chat.")
            broadcast_user_list()
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # מונע תקיעת פורט
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_sock, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    start_server()