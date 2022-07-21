import requests
from datetime import datetime
from sqlalchemy.orm import Session

from . import models


def save_currency_rates(db: Session, currency_pairs: list):
    # Updates currency exchange rates and saves them to the db
    for pair in currency_pairs:
        base = pair.split("/")[0]
        currency = pair.split("/")[1]
        url = f"https://api.exchangerate.host/convert?from={base}&to={currency}&amount=100&places=2"
        response = requests.get(url)
        db.add(
            models.CurrencyPair(
                date=datetime.now(),
                pair=pair,
                exchange_rate=response.json().get("info")["rate"],
            )
        )
    db.commit()


def get_currency_rate(currency_pairs: list, upwork_exchange_rate: float = None) -> dict:
    """
    Returns dict -> "currency_pair": "response.json()"
    """
    data = dict()
    for pair in currency_pairs:
        base = pair.split("/")[0]
        currency = pair.split("/")[1]
        url = (
            f"https://api.exchangerate.host/convert?from={base}&to={currency}&places=2"
        )
        response = requests.get(url)
        data[pair] = response.json()
    if upwork_exchange_rate:
        data["USD/RUB"] = upwork_exchange_rate
    return data


def currency_exchange_message(data: dict) -> str:
    """
    Returns message for TG bot:
    "currency_pair": "exchange rate"
    """
    message = []
    for pair, response_json in data.items():
        message.append(f'{pair}: {response_json.get("info")["rate"]}')
    return "\n".join(message)


def exchange_advice_message(data: dict) -> str:
    usd_rub = data.get("USD/RUB")
    for k, v in data.items():
        print(f"{k}:{v}")
        if k == "USD/TRY":
            usd_try = v.get("result")
        if k == "USD/RUB" and not isinstance(v, float):
            usd_rub = v.get("result")
        if k == "TRY/RUB":
            try_rub = v.get("info")["rate"]

    res_rub = usd_rub / try_rub

    message = (
        ["Сейчас выгоднее выводить через RUB 🇷🇺\n"]
        if res_rub >= usd_try
        else ["Сейчас выгоднее выводить через USD 🇺🇸\n"]
    )
    message.append(
        f"100$ через RUB: {round(res_rub, 2)*100}\n100$ через USD: {round(usd_try, 2)*100}"
    )
    return "\n".join(message)
