import requests
import random
import time

BASE_URL = "http://localhost:5000"

def register_analyzers(n=4):
    print("Registering analyzers...")
    for i in range(1, n + 1):
        data = {
            "analyzer_id": f"analyzer_{i}",
            "weight": round(random.uniform(0.1, 1.0), 2),
            "limit": random.randint(5, 15)
        }
        try:
            r = requests.post(f"{BASE_URL}/register_analyzer", json=data)
            print(f"Analyzer {i} response:", r.json())
        except Exception as e:
            print(f"Error: {e}")
            print("Response:", r.status_code if 'r' in locals() else 'No response')
            print("Text:", r.text if 'r' in locals() else 'No text')


def upload_packets(m=100):
    print("Uploading packets...")
    toggle_points = {m // 4, (3 * m) // 4}  
    
    for i in range(1, m + 1):
        data = {
            "packet_id": f"packet_{i}",
            "logs": f"Sample log message {i}",
            "duration": str(random.randint(5, 50))
        }
        try:
            r = requests.post(f"{BASE_URL}/upload_packet", json=data)
            print(f"Packet {i} response:", r.json())
            
            if i in toggle_points:
                print(f"\n Toggling a random analyzer at packet {i}")
                toggle_random_analyzers(n=1)

            time.sleep(0.2)

        except Exception as e:
            print(f"Error: {e}")
            print("Response:", r.status_code if 'r' in locals() else 'No response')
            print("Text:", r.text if 'r' in locals() else 'No text')



def toggle_random_analyzers(n=1):
    print(f"Toggling {n} random analyzer(s)...")

    for _ in range(n):
        analyzer_id = f"analyzer_{random.randint(1, 5)}"
        data = {
            "analyzer_id": analyzer_id
        }
        try:
            r = requests.post(f"{BASE_URL}/toggle_analyzer", json=data)
            r.raise_for_status()
            print(f"Toggled {analyzer_id}. Server Response:", r.json())
        except requests.exceptions.RequestException as e:
            print(f"Error toggling {analyzer_id}: {e}")


            
if __name__ == "__main__":
    requests.delete(f"{BASE_URL}/reset")
    register_analyzers(n=5)
    time.sleep(1)
    upload_packets(m=100)
