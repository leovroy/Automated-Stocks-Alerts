import requests
import smtplib
import sys
import os
import datetime as dt
from color import TextColor


t = TextColor()

credentials = {
        "email": os.environ.get("email"),
        "password" : os.environ.get("emailpassword"),
        "stock_api_key": os.environ.get("stckapikey"),
            }

stocks = {
        "Tesla": "TSLA",
        "Nike": "NKE",
        }


def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "--check":
            check_status()
            print()
            print(f"{t.green}{t.bold}- status checked ! -{t.end}")
        else:
            raise(ValueError(f"{t.red}{t.bold}Incorrect argument!{t.end}"))
    else:
        raise(ValueError(f"{t.red}{t.bold}Missing argument!{t.end}"))


def stck_fn(symbol, date):
    """stock function returns the closing price of the mentioned stock at the given date."""
    stck_params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": credentials["stock_api_key"]
                }
    r = requests.get(url="https://www.alphavantage.co/query", params=stck_params)
    return r.json()["Time Series (Daily)"][date]["4. close"]


def date_fn(n):
    """date function takes in one argument (n) to change the date as needed.
       n = 0 : present day, n = 1 : yesterday & as n increases it goes back."""
    present_tm = dt.datetime.now()
    year = present_tm.strftime("%Y")
    month = present_tm.strftime("%m")
    day = int(present_tm.strftime("%d")) - n
    if day < 10:
        day = f"0{day}"
    return f"{year}-{month}-{day}"


def mail(email, password, contents):
    """ takes 3 arguments & sends email to the said user """
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=email, password=password)
        connection.sendmail(
                from_addr = email,
                to_addrs = email,
                msg = f"Subject: Stocks Portfolio Status\n\n{contents}"
                    )


def check_status():
    """checks the present status of the stocks & sends mail if any stocks has any 
    considerable changes in their value"""
    for stck, value in stocks.items():
        if dt.datetime.now().weekday() == 6:
            c_stck_price = stck_fn(value, date_fn(2))
            p_stck_price = stck_fn(value, date_fn(3))
        elif dt.datetime.now().weekday() == 0:
            c_stck_price = stck_fn(value, date_fn(3))
            p_stck_price = stck_fn(value, date_fn(4))
        else:
            c_stck_price = stck_fn(value, date_fn(1))
            p_stck_price = stck_fn(value, date_fn(2))
        percent_diff = ((float(c_stck_price) - float(p_stck_price)) / float(c_stck_price)) * 100
        if percent_diff > 1:
            content = f"{stck} stock increased +{abs(percent_diff)}% in value."
            print(f"{t.green}{t.bold}{content}{t.end}")
            mail(credentials["email"], credentials["password"], content)
        elif percent_diff < -1:
            content = f"{stck} stock decreased -{abs(percent_diff)}% in value."
            print(f"{t.green}{t.bold}{content}{t.end}")
            mail(credentials["email"], credentials["password"], content)
        else:
            continue


if __name__ == "__main__":
    main()

