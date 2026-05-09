import socket

HOST = '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

print("Server is running...")

client_socket, client_address = server.accept()

print(f"Connected with {client_address}")

client_socket.send("Welcome to the server!".encode())

client_socket.close()
server.close()