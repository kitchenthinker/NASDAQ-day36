import smtplib
import datetime as dt_lib
import psw
import requests

# CONST
SMTP_PROVIDER = "smtp.mail.ru"
SMTP_PORT = 465
SMTP_SSL = True
NEWS_API_URL = "https://newsapi.org/v2/everything"
STOCK_API_URL = "https://www.alphavantage.co/query"
COMPANY_NAME_STOCK = "TSLA"
COMPANY_NAME_NEWS = "Tesla Inc"


def send_email(v_msg, v_title, v_from_addr=psw.MAIL_LOGIN, v_to_addr=psw.MAIL_TO_ADDRESS):
    """
    v_from_addr = your email address which will be used for sending email.
    v_to_addr = an email-address of recipient
    v_msg = your message
    """
    msg_header = f'From: Sender Name <{v_from_addr}>\n' \
                 f'To: Receiver Name <{v_to_addr}>\n' \
                 f'MIME-Version: 1.0\n' \
                 f'Content-type: text/html\n' \
                 f'Subject: {v_title}\n'
    msg_content = v_msg
    msg_full = ('\n'.join([msg_header, msg_content])).encode()
    with smtplib.SMTP_SSL(host=SMTP_PROVIDER, port=SMTP_PORT, timeout=5000) as connection:
        connection.login(user=psw.MAIL_LOGIN, password=psw.MAIL_PASSWORD)
        connection.sendmail(from_addr=v_from_addr, to_addrs=v_to_addr, msg=msg_full)


def get_news_data(name_request=COMPANY_NAME_NEWS, from_date=dt_lib.date.today()) -> []:
    news_params = {
        "q": name_request,
        "from": from_date,
        "sortBy": "popularity",
        "apiKey": psw.NEWS_API_KEY,
    }
    response = requests.get(url=NEWS_API_URL, params=news_params)
    try:
        response.raise_for_status()
    except Exception as e:
        print('Have some trouble during fetching data: ' + str(e))
        return None
    return response.json()["articles"]


def get_stock_data(name_request=COMPANY_NAME_STOCK) -> []:
    news_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": name_request,
        "outputsize": "compact",
        "apikey": psw.ALPHA_VANTAGE_KEY,
    }
    response = requests.get(url=STOCK_API_URL, params=news_params)
    try:
        response.raise_for_status()
    except Exception as e:
        print('Have some trouble during fetching data: ' + str(e))
        return None
    data = response.json()["Time Series (Daily)"]
    days_that_we_need = list(data)[:2]
    list_of_data = [value for (key, value) in data.items() if key in days_that_we_need]
    return list_of_data


def check_stock_data(datum: [], difference_min=5):
    if len(datum) != 2:
        return False

    dict_2_return = {
        "is_change": False,
        "percent": 0,
        "increase": False,
    }
    yesterday = datum[0]
    before_yesterday = datum[-1]
    a_value = float(yesterday["4. close"])
    b_value = float(before_yesterday["4. close"])
    difference = abs(a_value - b_value)
    percent = round((difference / a_value) * 100, 2)
    if percent > difference_min:
        dict_2_return["is_change"] = True
        dict_2_return["percent"] = percent
        dict_2_return["increase"] = (a_value - b_value) > 0
    return dict_2_return


def get_letter_body(stock_data, news_data) -> str:
    msg_text = ""
    msg_text += f"Hello, I have got some news for you\n"
    if stock_data["increase"]:
        msg_text += f"{COMPANY_NAME_STOCK}: ↑{stock_data['percent']}%\n"
    else:
        msg_text += f"{COMPANY_NAME_STOCK}: ↓{stock_data['percent']}%\n"

    msg_text += "Here's some news about it:\n\n"

    for news in news_data[:3]:
        link_2_news = news['url']
        msg_text += f"<h3>Headline: {news['title']}</h3>\n"
        msg_text += f"<h4>Brief: {news['description']}</h4>\n"
        msg_text += f'<a href="{link_2_news}">The Link</a>\n\n'

    return msg_text


def main_func():
    stock_data = get_stock_data()
    checking_data = check_stock_data(stock_data, 1)
    if checking_data["is_change"]:
        news_data = get_news_data()
        letter_body = get_letter_body(checking_data, news_data)
        send_email(v_msg=letter_body, v_title=f"Hey, mate. I have news for you about {COMPANY_NAME_NEWS}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main_func()
