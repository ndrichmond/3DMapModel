import subprocess
import time
import requests

# --- CONFIG ---
LAN_IP = "10.0.0.145"  # Replace with your LAN IP
PORT = 8080

# --- Start ngrok ---
print(f"Starting ngrok tunnel to http://{LAN_IP}:{PORT} ...")
ngrok_process = subprocess.Popen(["ngrok", "http", f"http://{LAN_IP}:{PORT}"])

# --- Wait a few seconds for ngrok to initialize ---
time.sleep(5)

# --- Query ngrok API for public URL ---
try:
    api_url = "http://127.0.0.1:4040/api/tunnels"
    response = requests.get(api_url).json()
    tunnels = response.get("tunnels", [])
    if not tunnels:
        print("No tunnels found. Is ngrok running?")
    else:
        for tunnel in tunnels:
            print("Public URL:", tunnel["public_url"])
except requests.exceptions.RequestException as e:
    print("Could not contact ngrok API:", e)

# --- Keep script running if you want ngrok alive ---
print("ngrok is running. Press Ctrl+C to stop.")
try:
    ngrok_process.wait()
except KeyboardInterrupt:
    print("Stopping ngrok...")
    ngrok_process.terminate()