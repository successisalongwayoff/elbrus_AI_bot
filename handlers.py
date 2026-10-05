from aiogram import Router,F
from aiogram.filters import CommandStart,Command
from weather_api import LOCATIONS, get_weather
from keyboards import get_locations_keyboard
from aiogram.types import CallbackQuery
from predict import predict_ascent_safety, format_weather_message
import pandas as pd
router = Router()

@router.message(CommandStart())
@router.message(Command("weather"))
async def cmd_weather(message):
    await message.answer("Выберите локацию на Эльбрусе для получения текущей погоды: ",
                         reply_markup = get_locations_keyboard())
@router.callback_query(F.data.startswith('loc_'))
async def process_location_callback(callback:CallbackQuery):
    loc_key = callback.data.replace("loc_", "")
    if loc_key not in LOCATIONS:
        await callback.answer("Локация не найдена!",show_alert=True)
        return
    location_info = LOCATIONS[loc_key]
    await callback.answer("Загружаю данные погоды....")

    try:
        data = await get_weather(loc_key)
        hourly_dict = data["hourly"]
        hourly_df = pd.DataFrame(hourly_dict)

        hourly_df["elevation"] = location_info["elevation"]

        prepared_df = predict_ascent_safety(hourly_df)

        text = format_weather_message(location_info["name"], prepared_df)

        await callback.message.edit_text(
            text, reply_markup=get_locations_keyboard(),parse_mode="Markdown"
        )
    except Exception as e:
        print(f"ОШИБКА В HELDERS: {e}")
        await callback.message.answer(f"Ошибка при обработке данных: {e}")