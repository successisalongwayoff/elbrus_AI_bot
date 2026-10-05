import asyncio
import httpx
import pandas as pd
from weather_api import LOCATIONS

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


async def fecth_history_for_location(
    client: httpx.AsyncClient, loc_key: str, loc_data: dict
) -> pd.DataFrame:
    params = {
        "latitude": loc_data["lat"],  # Теперь lat берется из LOCATIONS
        "longitude": loc_data["lon"],  # И lon тоже
        "elevation": loc_data["elevation"],
        "start_date": "2023-01-01",
        "end_date": "2026-09-01",
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
            "wind_gusts_10m",
        ],
        "wind_speed_unit": "ms",
        "timezone": "auto",
    }
    print(
        f"Загружаем историю для: {loc_data['name']} ({loc_data['elevation']} м)..."
    )
    response = await client.get(ARCHIVE_URL, params=params, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["hourly"])

    df["location_key"] = loc_key
    df["location_name"] = loc_data["name"]
    df["elevation"] = loc_data["elevation"]
    return df


async def main():
    # Просто берем LOCATIONS из weather_api.py — там уже есть все 5 точек с lat/lon
    all_dfs = []
    async with httpx.AsyncClient() as client:
        for loc_key, loc_data in LOCATIONS.items():
            df = await fecth_history_for_location(client, loc_key, loc_data)
            all_dfs.append(df)

    full_df = pd.concat(all_dfs, ignore_index=True)

    output_filename = "elbrus_all_locations_history.csv"
    full_df.to_csv(output_filename, index=False)
    print(f"\nГотово! Все данные сохранены в файл: {output_filename}")


if __name__ == "__main__":
    asyncio.run(main())