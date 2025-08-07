import requests

API_KEY = "ak_live_de21c77b84b9535c004f8f6d61959cfe2aa1370565aa36ab"
BASE_URL = "http://3.80.223.142:3001/api/"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def get_catalogo_cuentas():
    try:
        response = requests.get(f"{BASE_URL}public/catalogo-cuentas", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_entradas_contables():
    try:
        response = requests.get(f"{BASE_URL}public/entradas-contables", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def crear_entrada_contable(data):
    try:
        response = requests.post(f"{BASE_URL}public/entradas-contables", headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
