import requests
import json
import threading

API_URL = "http://localhost:8080"


def get_request(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {
            "error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."
        }
    except Exception as e:
        return 500, {"error": str(e)}


def post_request(endpoint, data):
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {
            "error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."
        }
    except Exception as e:
        return 500, {"error": str(e)}


def put_request(endpoint, data):
    try:
        response = requests.put(f"{API_URL}{endpoint}", json=data, timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {
            "error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."
        }
    except Exception as e:
        return 500, {"error": str(e)}


def delete_request(endpoint):
    try:
        response = requests.delete(f"{API_URL}{endpoint}", timeout=5)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 500, {
            "error": "No se pudo conectar con el servidor Go. Verifica que esté encendido."
        }
    except Exception as e:
        return 500, {"error": str(e)}
    
def listen_events(on_event, stop_event):
    try:
        with requests.get(f"{API_URL}/api/events", stream=True, timeout=30) as response:
            if response.status_code != 200:
                return

            current_event = None

            for line in response.iter_lines(decode_unicode=True):
                if stop_event.is_set():
                    break

                if not line:
                    continue

                if line.startswith("event:"):
                    current_event = line.replace("event:", "").strip()

                elif line.startswith("data:"):
                    raw_data = line.replace("data:", "").strip()

                    try:
                        data = json.loads(raw_data)
                    except Exception:
                        data = {}

                    if current_event:
                        on_event(current_event, data)

    except Exception:
        pass


def start_event_listener(on_event):
    stop_event = threading.Event()

    thread = threading.Thread(
        target=listen_events,
        args=(on_event, stop_event),
        daemon=True
    )

    thread.start()

    return stop_event