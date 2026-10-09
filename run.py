from waitress import serve
from app import app  # replace 'app' with your Flask module

if __name__ == "__main__":
    host_ip = "10.0.0.145" 
    port = 8080
    threads = 50  

    print(f"Starting Waitress server on http://{host_ip}:{port} with {threads} threads...")
    serve(app, host=host_ip, port=port, threads=threads)

