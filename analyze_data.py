import pandas as pd

df = pd.read_csv("elbrus_all_locations_history.csv")

print("--- ОБЩАЯ ИНФОРМАЦИЯ О ДАТАСЕТЕ ---")
print(f"Всего строк в таблице: {len(df)}")
print(f"Список колонок: {list(df.columns)}")
print("\nПервые 5 строк:")
print(df.head())

print("\n--- ПРОВЕРКА ПРОПУСКОВ ---")
print(df.isnull().sum())

peak_df = df[df["location_key"] == "peak"].copy()

def check_safety(row):
    elevation = row["elevation"]

    if elevation >= 5000:
        max_wind = 10.0
        max_gusts = 15.0
        min_temp = -25.0
    elif elevation >= 3700:
        max_wind = 10.0
        max_gusts = 15.0
        min_temp = -25.0
    else:
        # Азау / Чегет (нижняя зона)
        max_wind = 15.0
        max_gusts = 22.0
        min_temp = -15.0

    is_wind_ok = row["wind_speed_10m"] <= max_wind
    is_gusts_ok = row["wind_gusts_10m"] <= max_gusts
    is_temp_ok = row["apparent_temperature"] >= -28.0
    is_precip_ok = row["precipitation"] <= 0.5
    

    return int(is_wind_ok and is_gusts_ok and is_temp_ok and is_precip_ok)

df['is_safe_current'] = df.apply(check_safety, axis=1)
print("Создаем лаговые признаки и динамику изменений...")
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values(["location_key", "time"]).reset_index(drop=True)
df["target_safe_1h"] = df.groupby("location_key")["is_safe_current"].shift(-1)

indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=10)
df["target_safe_10h"] = (
    df.groupby("location_key")["is_safe_current"]
    .transform(lambda x: x.rolling(window=indexer, min_periods=10).sum()) == 10
).astype(int)
df['wind_speed_lag1'] = df.groupby("location_key")["wind_speed_10m"].shift(1)

df["wind_gusts_lag1"] = df.groupby("location_key")["wind_gusts_10m"].shift(1)

df["temp_lag1"] = df.groupby("location_key")["apparent_temperature"].shift(1)

df["wind_trend"] = df["wind_speed_10m"] - df["wind_speed_lag1"]

df["gusts_trend"] = df["wind_gusts_10m"] - df["wind_gusts_lag1"]

df["temp_trend"] = df["apparent_temperature"] - df["temp_lag1"]

df = df.dropna().reset_index(drop=True)

df["target_safe_1h"] = df["target_safe_1h"].astype(int)
df["target_safe_10h"] = df["target_safe_10h"].astype(int)


output_filename = "elbrus_all_locations_labeled.csv"
df.to_csv(output_filename, index=False)
print(f"\nРазмеченный датасет сохранен в: {output_filename}")