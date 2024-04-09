import socket
import threading
import requests
import json
import time

# Discover Server Address
DISCOVERY_SERVER = "http://127.0.0.1:4900"

def register_with_discovery_server(user_id, local_port):
    address = f"127.0.0.1:{local_port}"
    try:
        response = requests.post(f"{DISCOVERY_SERVER}/register", json={"user_id": user_id, "address": address})
        print("Registered with the discovery server successfully." if response.ok else "Failed to register with the discovery server.")
    except Exception as e:
        print(f"Error registering with discovery server: {e}")

# Look up users
def lookup_user(user_id):
    try:
        response = requests.get(f"{DISCOVERY_SERVER}/lookup/{user_id}")
        if response.status_code == 200:
            data = response.json()
            return data["address"], 'online', data.get("last_seen", "")
        elif response.status_code == 404:
            return None, 'not found', None
    except Exception as e:
        print(f"Error looking up user: {e}")
    return None, 'error', None

# Constant listening for incoming messages
def listen_for_messages(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"Listening for connections on port {port}...")
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Client Socket
def handle_client(client_socket):
    with client_socket as sock:
        while True:
            message = sock.recv(1024)
            if not message:
                break
            print(f"Received message: {message.decode('utf-8')}")

# Send messages 
def send_message(target_address, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((target_address.split(':')[0], int(target_address.split(':')[1])))
            sock.sendall(message.encode('utf-8'))
            print("Message sent successfully.")
        except Exception as e:
            print(f"Failed to send message: {e}")

def main():
    user_id = input("Enter your user ID: ")
    local_port = int(input("Enter your listening port: "))
    register_with_discovery_server(user_id, local_port)

    listening_thread = threading.Thread(target=listen_for_messages, args=(local_port,))
    listening_thread.start()

    # Delay for initialization
    time.sleep(1)
    print("Initialized...")

    # I/O 
    while True:
        peer_user_id = input("\nEnter peer's user ID to chat with, or 'exit' to quit: ")
        if peer_user_id.lower() == 'exit':
            break
        if peer_user_id == user_id:
            print("ERROR: Can't message yourself! Please enter a valid User ID.")
            continue

        address, status, last_seen = lookup_user(peer_user_id)
        if address:
            print(f"User {peer_user_id} is online! You can start messaging, or 'back' to select new user.")
            while True:
                message = input()
                if message.lower() == 'back':
                    break
                send_message(address, message)
        elif status == 'not found':
            print(f"ERROR: User {peer_user_id} not found! Please enter a valid User ID.")
        elif status == 'offline':
            print(f"User {peer_user_id} is offline. Last seen: {last_seen}")
        else:
            print("ERROR: There was an error. Please try again.")

if __name__ == "__main__":
    main()
