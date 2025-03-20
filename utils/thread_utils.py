import time
import socket

# Server
def server_networking_thread(sock, buffer_size, network_queue, players, DEBUG=False):
    print("Starting networking thread...")
    while True:
        try:
            # Receive data from players
            data, addr = sock.recvfrom(buffer_size)
            
            # Check if the player is already registered
            if addr not in players.values():
                continue
            
            # Add received data to the queue
            network_queue.put((data, addr))
        except socket.error:
            pass

def server_latency_thread(latency_sock, buffer_size, DEBUG=False):
    """Thread to handle latency checks."""
    print("Starting latency thread...")
    while True:
        try:
            # Wait for latency check messages
            data, addr = latency_sock.recvfrom(buffer_size)
            if data == b"latency_check":
                # Respond with latency response
                latency_sock.sendto(b"latency_response", addr)
                if DEBUG:
                    print(f"Latency check received from {addr}, responded with latency_response")
        except socket.error as e:
            if DEBUG:
                print(f"Latency socket error: {e}")


# Client
def client_networking_rec_thread(sock, buffer_size, network_queue, DEBUG=False):
    if DEBUG: print("Starting networking thread...")
    while True:
        try:
            data, addr = sock.recvfrom(buffer_size)
            network_queue.put((data, addr))  # Add received data to the queue
        except socket.error:
            pass

def client_latency_thread(sock, buffer_size, server_ip, latency_port, latency_queue, interval=0.5, DEBUG=False):
    """Thread to measure latency periodically."""
    if DEBUG: print(f"Starting latency thread with {interval} s interval...")
    while True:
        start_time = time.time()
        try:
            # Send a latency check message
            sock.sendto(b"latency_check", (server_ip, latency_port))
            
            # Wait for the server's response
            data, addr = sock.recvfrom(buffer_size)
            if data == b"latency_response":
                latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                latency_queue.put(latency)  # Store latency in the queue
                if DEBUG: print(f"Latency: {latency:.2f} ms")
        except socket.error:
            pass
        
        time.sleep(interval)  # Wait before the next check