import requests

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