import requests

def fire_request(method, url, headers, body):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=body, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=body, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        return response, None
    except requests.exceptions.ConnectionError:
        return None, "Connection Error — URL unreachable or invalid"
    except requests.exceptions.Timeout:
        return None, "Timeout — server took more than 10 seconds"
    except Exception as e:
        return None, str(e)