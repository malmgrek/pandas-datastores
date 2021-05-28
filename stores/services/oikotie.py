import requests


if __name__ == "__main__":
    session = requests.Session()
    res = session.get("https://asunnot.oikotie.fi/user/get?format=json")
    cookies = session.cookies.get_dict()
    user = res.json().get("user")
    ota_token = user["token"]
    ota_loaded = str(user["time"])
    ota_cuid = cookies["user_id"]
    headers = {
        "OTA-token": ota_token,
        "OTA-loaded": ota_loaded,
        "OTA-cuid": ota_cuid,
    }
    url = (
        "https://asunnot.oikotie.fi/api/cards?"
        "cardType=100&limit=24&locations=%5B%5B335117,4,%22Kivikko,+Helsinki%22%5D%5D&offset=0&sortBy=published_sort_desc"
    )
    res = requests.get(url, headers=headers)
    print("OTA-token: {}".format(ota_token))
    print("OTA-loaded: {}".format(ota_loaded))
    print("OTA-cuid: {}".format(ota_cuid))
    print(res)
