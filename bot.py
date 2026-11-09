import asyncio
import logging
import requests
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

# ВСТАВЬ СЮДА СВОИ ДАННЫЕ
TOKEN = "9259216256:AAGAWNQexWsQ38CxjaPVx1bi9Hh8mf28I7c"
WEATHER_KEY = "86ce8c8cde65aeebef676cfe"
RATE_KEY = "1e7ffce59f62762077612b5c3a8b5892"

logging.basicConfig(level=logging.INFO)
session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# --- КЭШИРОВАНИЕ (на 5 минут) ---
cache = {}
def get_cache(key):
    if key in cache and time.time() - cache[key][1] < 300:
        return cache[key][0]
    return None
def set_cache(key, value):
    cache[key] = (value, time.time())

# --- КОМАНДА КУРСА ВАЛЮТ ---
@dp.message(Command("rate"))
async def cmd_rate(message: types.Message):
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Формат: /rate USD RUB")
        return
    
    base, target = args[1].upper(), args[2].upper()
    cache_key = f"rate_{base}_{target}"
    
    # Проверяем кэш
    cached_result = get_cache(cache_key)
    if cached_result:
        await message.answer(f"{cached_result}\n(Взято из кэша)")
        return
    
    try:
        url = f"https://v6.exchangerate-api.com/v6/{RATE_KEY}/pair/{base}/{target}"
        resp = requests.get(url).json()
        
        if resp.get("result") == "success":
            rate = resp["conversion_rate"]
            text = f"1 {base} = {rate} {target}"
            set_cache(cache_key, text)
            await message.answer(text)
        else:
            await message.answer("Ошибка: неверный код валюты.")
    except Exception:
        await message.answer("Ошибка API. Попробуйте позже.")

# --- КОМАНДА ПОГОДЫ ---
@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer("Формат: /weather Москва")
        return
    
    city = args[1]
    cache_key = f"weather_{city.lower()}"
    
    cached_result = get_cache(cache_key)
    if cached_result:
        await message.answer(f"{cached_result}\n(Взято из кэша)")
        return
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=ru"
        resp = requests.get(url).json()
        
        if resp.get("cod") == 200:
            temp = resp["main"]["temp"]
            desc = resp["weather"][0]["description"]
            text = f"Погода в {city}: {temp}°C, {desc}"
            set_cache(cache_key, text)
            await message.answer(text)
        else:
            await message.answer("Город не найден.")
    except Exception:
        await message.answer("Ошибка API. Попробуйте позже.")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот погоды и валют.\nПиши /rate USD RUB или /weather Москва")

async def main():
    print("Бот погоды и валют запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())