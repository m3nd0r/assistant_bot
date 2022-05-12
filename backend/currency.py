import requests


def get_currency_rate(currency_pairs: list) -> dict:
    """
    Returns dict -> "currency_pair": "response.json()"
    """
    res = dict()
    for pair in currency_pairs:
        base = pair.split("/")[0]
        currency = pair.split("/")[1]
        url = f"https://api.exchangerate.host/convert?from={base}&to={currency}&amount=100&places=2"
        response = requests.get(url)
        res[pair] = (response.json())
    return res


def currency_exchange_message(data: dict) -> str:
    """
    Returns message for TG bot:
    "currency_pair": "exchange rate"
    """
    message = []
    for pair, responsse_json in data.items():
        message.append(f'{pair}: {responsse_json.get("info")["rate"]}')
    return '\n'.join(message)


def exchange_advice_message(data: dict) -> str:
    for k, v in data.items():
        if k == "USD/TRY":
            usd_try = v.get("result") - 100
        if k == "USD/RUB":
            usd_rub = v.get("result") - 300
        if k == "TRY/RUB":
            try_rub = v.get("info")["rate"]
    res_rub = usd_rub/try_rub

    message = ["Сейчас выгоднее выводить через RUB."] if res_rub >= usd_try else ["Сейчас выгоднее выводить через USD"]
    message.append(f"100$ через RUB: {round(res_rub, 2)}\n100$ через USD: {round(usd_try, 2)}")
    return '\n'.join(message)
