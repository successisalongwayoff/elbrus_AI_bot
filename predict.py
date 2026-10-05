import joblib
import pandas as pd

model_1h = joblib.load("ascent_model_1h.pkl")
model_10h = joblib.load("ascent_model_10h.pkl")

FEATURE_COLS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
    "wind_gusts_10m",
    "elevation",
    "wind_speed_lag1",
    "wind_gusts_lag1",
    "temp_lag1",
    "wind_trend",
    "gusts_trend",
    "temp_trend",
]

def prepare_features(hourly_df: pd.DataFrame) -> pd.DataFrame:
    df = hourly_df.copy()

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["wind_speed_lag1"] = df["wind_speed_10m"].shift(1).fillna(df["wind_speed_10m"])
    df["wind_gusts_lag1"] = df["wind_gusts_10m"].shift(1).fillna(df["wind_gusts_10m"])
    df["temp_lag1"] = df["apparent_temperature"].shift(1).fillna(df["apparent_temperature"])

    df["wind_trend"] = df["wind_speed_10m"] - df["wind_speed_lag1"]
    df["gusts_trend"] = df["wind_gusts_10m"] - df["wind_gusts_lag1"]
    df["temp_trend"] = df["apparent_temperature"] - df["temp_lag1"]



    return df

def predict_ascent_safety(hourly_df: pd.DataFrame) -> pd.DataFrame:
    dp_prepared = prepare_features(hourly_df)
    X = dp_prepared[FEATURE_COLS]

    dp_prepared['prob_safe_1h'] = (model_1h.predict_proba(X)[:, 1]*100).round(1)
    dp_prepared["prob_safe_10h"] = (model_10h.predict_proba(X)[:,1]*100).round(1)

    return dp_prepared

def format_weather_message(location_name:str, prepared_df:pd.DataFrame) -> str:
    row = prepared_df.iloc[0]

    prob_1h = row["prob_safe_1h"]
    prob_10h = row["prob_safe_10h"]

    if prob_10h >= 75:
        status_10h = '🟢 БЕЗОПАСНО ДЛЯ ШТУРМА'
    elif prob_10h >= 50:
        status_10h = "🟡 ВЫСОКИЙ РИСК (Следите за динамикой)"
    else:
        status_10h = "🔴 ОПАСНО (Штурм сорван/не рекомендуется)"

    text = (
        f"🏔️ **Прогноз погоды: {location_name}**\n"
        f"🕒 Время: `{row['time'].strftime('%Y-%m-%d %H:%M')}`\n\n"
        f"🌡 Температура: **{row['temperature_2m']}°C** (ощущается как {row['apparent_temperature']}°C)\n"
        f"💨 Ветер: **{row['wind_speed_10m']} км/ч** (порывы до **{row['wind_gusts_10m']} км/ч**)\n"
        f"💧 Влажность: **{row['relative_humidity_2m']}%** | Осадки: **{row['precipitation']} мм**\n\n"
        f"🤖 **ИИ-АНАЛИЗ БЕЗОПАСНОСТИ (ML):**\n"
        f"• Оценка на 1 час: **{prob_1h}%** safe\n"
        f"• Окно штурма (10 часов): **{prob_10h}%** safe\n\n"
        f"**Вердикт на штурм:**\n{status_10h}"
    )
    return text