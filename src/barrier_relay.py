import requests
from http import HTTPStatus


def open_barrier(url: str, user: str, password: str) -> bool:
    response = requests.get(url, auth=(user, password))

    if response.status_code == HTTPStatus.OK:
        return True
    
    return False
