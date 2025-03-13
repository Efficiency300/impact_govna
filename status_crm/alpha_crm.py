import requests
from config.config import Config
from datetime import date
def authenticate(base_url, username, password):
    """Функция для аутентификации в AlfaCRM API"""
    url = f"{base_url}/v2api/auth/login"
    payload = {
        "email": username,
        "api_key": password
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception(f"Ошибка аутентификации: {response.text}")


def make_request(base_url, token, endpoint, method="GET", data=None):
    """Функция для выполнения запросов к API AlfaCRM"""
    url = f"{base_url}/v2api/{endpoint}"
    headers = {"Authorization": f"Bearer {token}", "X-ALFACRM-TOKEN": token}

    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError("Метод запроса не поддерживается")

    return response.json()


def alfaintegration_code(data: dict):


    try:
        token = authenticate(Config.BASE_URL_ALPHA, Config.USERNAME_ALPHA, Config.PASSWORD_ALPHA)
        print("Успешная аутентификация, токен получен.")

        current_date = date.today()
        date_str = current_date.strftime("%Y-%m-%d")

        BRANCH = 1

        lead_data = {
            "name": data["name"],
            "legal_type": 1,  # Физическое лицо
            "is_study": 0,  # Лид, не клиент
            "phone": data["phone"],
            "note": data["note"],
            "created_at": date_str,  # Дата регистрации
            "branch_ids": [BRANCH],  # ID филиала
        }

        lead_response = make_request(Config.BASE_URL_ALPHA, token, f"{BRANCH}/customer/create", method="POST", data=lead_data)
        print("Создан новый лид:", lead_response)

    except Exception as e:
        print("Ошибка:", e)
