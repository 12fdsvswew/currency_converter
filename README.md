# Currency Converter

## Author
Митишев Данил 

## Description
GUI-приложение для конвертации валют с использованием внешнего API. Позволяет конвертировать суммы между различными валютами, сохраняет историю конвертаций и имеет удобный графический интерфейс.

## How to Get API Key

1. Перейдите на сайт: https://www.exchangerate-api.com/
2. Нажмите "Get Free API Key" (бесплатный тариф позволяет до 1500 запросов в месяц)
3. Зарегистрируйтесь с помощью email или Google-аккаунта
4. После регистрации скопируйте ваш API-ключ
5. В файле `currency_converter.py` замените `YOUR_API_KEY` на полученный ключ

## Installation & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd currency_converter

# Install dependencies
pip install -r requirements.txt

# Run application
python currency_converter.py
