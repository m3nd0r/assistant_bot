from currency import (
    get_currency_rate,
    currency_exchange_message,
    exchange_advice_message,
)
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/currency")
async def currency():
    data = get_currency_rate(currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"])
    return currency_exchange_message(data)


@app.get("/need_tl")
async def currency():
    """
    Считает, как выгоднее получить лиры - через рубли или через доллары на примере 100$
    100$ в лирах = 100* (15,31 -1) = 1431 tl
    100$ в рубли -> в лиры (66,76 - 3)*100/4.36=1462.12
    """
    data = get_currency_rate(currency_pairs=["USD/RUB", "USD/TRY", "TRY/RUB"])
    return exchange_advice_message(data)
