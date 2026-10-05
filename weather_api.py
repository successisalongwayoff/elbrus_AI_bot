import httpx

# Координаты точек на Эльбрусе
LOCATIONS = {
    "azau": {"name": "Поляна Азау", "elevation": 2350, "lat": 43.2685, "lon": 42.4783},
    "garabashi": {"name": "Станция Гарабаши", "elevation": 3847, "lat": 43.2975, "lon": 42.4602},
    "prijut11": {"name": "Приют 11", "elevation": 4100, "lat": 43.3101, "lon": 42.4568},
    "sedlovina": {"name": "Седловина Эльбруса", "elevation": 5416, "lat": 43.3499, "lon": 42.4453},
    "peak": {"name": "Вершина Эльбруса", "elevation": 5642, "lat": 43.3550, "lon": 42.4392},
}

async def get_weather(loc_key: str) -> dict:
    loc = LOCATIONS[loc_key]
    
    # URL с обязательным запросом hourly-параметров!
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={loc['lat']}&longitude={loc['lon']}"
        f"&hourly=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,wind_gusts_10m"
        f"&wind_speed_unit=ms"  # Метры в секунду
        f"&forecast_days=2"     # Берем запас на 2 дня вперед
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()