from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_locations_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🏔 Поляна Азау (2350м)", callback_data="loc_azau")],
        [InlineKeyboardButton(text="🏔 Станция Гарабаши (3847м)", callback_data="loc_garabashi")],
        [InlineKeyboardButton(text="🏔 Приют 11 (4100м)", callback_data="loc_prijut11")],
        [InlineKeyboardButton(text="🏔 Седловина (5416м)", callback_data="loc_sedlovina")],
        [InlineKeyboardButton(text="🏔 Вершина (5642м)", callback_data="loc_peak")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)