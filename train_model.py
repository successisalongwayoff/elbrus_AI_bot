import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

df = pd.read_csv("elbrus_all_locations_labeled.csv")

feature_cols = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
    "wind_gusts_10m",
    "elevation",
    "wind_speed_lag1",   # Ветер час назад
    "wind_gusts_lag1",   # Порывы час назад
    "temp_lag1",         # Температура час назад
    "wind_trend",        # Тренд ветра
    "gusts_trend",       # Тренд порывов
    "temp_trend",
]

df["time"] = pd.to_datetime(df['time'])

train_df = df[df["time"] < "2026-01-01"]
test_df = df[df["time"] >= "2026-01-01"]

X_train = train_df[feature_cols]


X_test = test_df[feature_cols]


# X_train, X_test, y_train, y_test = train_test_split(
#     X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
# )
print(f"Обучающих строк: {len(X_train)} | Тестовых строк: {len(X_test)}\n")

print("Обучаем модель RandomForestClassifier...")
print("=== [1/2] Обучение модели на 1 ЧАС (ascent_model_1h) ===")
y_train_1h = train_df["target_safe_1h"]
y_test_1h = test_df["target_safe_1h"]

model1_h = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)

model1_h.fit(X_train,y_train_1h)

y_pred_1h = model1_h.predict(X_test)
print(f"Точность (1 час): {accuracy_score(y_test_1h, y_pred_1h) * 100:.2f}%")
print(classification_report(y_test_1h, y_pred_1h, target_names=["Опасно", "Безопасно"]))

joblib.dump(model1_h, "ascent_model_1h.pkl")
print("Сохранено: ascent_model_1h.pkl\n")

print("=== [2/2] Обучение модели на 10 ЧАСОВ (ascent_model_10h) ===")

y_train_10h = train_df["target_safe_10h"]
y_test_10h = test_df["target_safe_10h"]

model10_h = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
model10_h.fit(X_train, y_train_10h)
y_pred_10h = model10_h.predict(X_test)

accuracy_10h = accuracy_score(y_test_10h, y_pred_10h)
print(f"\n--- РЕЗУЛЬТАТЫ ---")
print(f"Точность (Accuracy): {accuracy_10h * 100:.2f}%\n")
print(classification_report(y_test_10h, y_pred_10h, target_names=["Опасно (0)", "Безопасно (1)"]))

importance_df = pd.DataFrame(
     {"Feature" : feature_cols, "importance" : model10_h.feature_importances_}).sort_values(by="importance", ascending=False)

print("--- ВАЖНОСТЬ ПРИЗНАКОВ 10Ч---")
print(importance_df.to_string(index=False))
model_filename = "ascent_model.pkl"
joblib.dump(model10_h, "ascent_model_10h.pkl")
print("\nСохранено: ascent_model_10h.pkl")
print("\nВсе модели успешно обучены и сохранены!")
