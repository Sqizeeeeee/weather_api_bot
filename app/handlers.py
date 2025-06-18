from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from config import API
from text import greeting_text, help_text, info_text, commands_text, thanks_text, review_text, how_to_use_text
from datetime import datetime
import requests
import os








router = Router()

















@router.message(CommandStart()) # start function
async def cmd_start(message: Message):
    await message.answer(greeting_text)




'''weather block starts'''



awaiting_location = set()






def get_weather(location):
    '''here we implement weather finding process'''

    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": API,
        "q": location,
        "days": 1,       # прогноз на 1 день
        "lang": "ru",    # русский язык
        "aqi": "no",     # качество воздуха (no = выключено)
        "alerts": "no"   # предупреждения (no = выключено)
    }

    response = requests.get(url, params=params)
    data = response.json()


    if response.status_code == 200:
        forecast_day = data["forecast"]["forecastday"][0]["day"]
        current = data["current"]
        condition = current["condition"]["text"]
        temp_c = current["temp_c"]
        feelslike_c = current["feelslike_c"]
        rain_chance = forecast_day.get("daily_chance_of_rain", 0)

        return (
            f"Погода в {location}: температура {temp_c}°C\n"
            f"Ощущается как: {feelslike_c}°C\n"
            f"Вероятность дождя: {rain_chance}%"

        )


    else:
        return f"Ошибка: {data.get('error', {}).get('message', 'пункт не найден')}"








def weather_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="продолжить?", callback_data="weather_continue")],
        [InlineKeyboardButton(text="меню", callback_data="weather_exit")]
    ])

@router.message(Command("weather"))
async def cmd_weather(message: Message):
    await message.answer(how_to_use_text, reply_markup=weather_keyboard())

@router.callback_query(F.data == "weather_continue")
async def weather_continue(callback: CallbackQuery):
    user_id = callback.from_user.id
    awaiting_location.add(user_id)
    await callback.message.edit_text("Введите локацию:")
    await callback.answer()

@router.callback_query(F.data == "weather_exit")
async def weather_exit(callback: CallbackQuery):
    user_id = callback.from_user.id
    awaiting_location.discard(user_id)
    await callback.message.edit_text("Вы в главном меню.")
    await callback.answer()

@router.message(lambda message: message.from_user.id in awaiting_location)
async def process_location(message: Message):
    user_id = message.from_user.id
    location = message.text.strip()

    if location.startswith("/"):
        await message.answer("Пожалуйста, введи название города, а не команду.")
        return

    awaiting_location.remove(user_id)
    weather_report = get_weather(location)
    await message.answer(weather_report)







'''weather block ends'''



@router.message(Command("help")) #help function
async def cmd_help(message: Message):
    await message.answer(help_text)


@router.message(Command("info")) #info function
async def cmd_info(message: Message):
    await message.answer(info_text)

@router.message(Command("commands")) #commands function
async def cmd_commands(message: Message):
    await message.answer(commands_text)

'''review block starts'''

CURRENT_DIR = os.path.dirname(__file__)
REVIEW_PATH = os.path.join(CURRENT_DIR, '..', 'review.txt')

waiting_for_review = set()

@router.message(Command("review"))
async def cmd_review(message: Message):
    user_id = message.from_user.id
    waiting_for_review.add(user_id)
    await message.answer(review_text)

@router.message(lambda message: message.from_user.id in waiting_for_review)
async def catch_review(message: Message):
    user_id = message.from_user.id
    review_text = message.text
    user_name = message.from_user.full_name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(REVIEW_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {user_name} (ID: {user_id}): {review_text}\n")

    await message.answer(thanks_text)
    waiting_for_review.remove(user_id)

'''rewiew block ends'''
