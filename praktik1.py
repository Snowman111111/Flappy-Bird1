python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#🟥 1. Получение Dataset (генерация случайных чисел)
np.random.seed(42)  # для воспроизводимости
data = np.random.randint(-10000, 10001, size=1000)
series = pd.Series(data)

#🟥 2. Расчет статистических характеристик
median_value = series.median()
mean_value = series.mean()
greaterthanmean = series[series > mean_value].count()
min_value = series.min()
std_dev = series.std()
rolling_mean = series.rolling(window=37).mean()

#🟥 3. Вывод результатов
print(f"Медиана ряда: {median_value}")
print(f"Количество чисел, больше среднего: {greaterthanmean}")
print(f"Минимальное значение: {min_value}")
print(f"Среднеквадратическое отклонение: {std_dev:.2f}")

#🟥 4. Визуализация данных
#🟥 Линейный график
plt.figure(figsize=(10, 4))
plt.plot(series, label='Исходные данные')
plt.title('Линейный график данных')
plt.xlabel('Индекс')
plt.ylabel('Значение')
plt.legend()
plt.show()

#🟥 Гистограмма с округлением до сотен по математическому правилу
rounded_data = np.round(series / 100).astype(int) * 100
plt.figure(figsize=(10, 4))
plt.hist(roundeddata, bins=range(roundeddata.min(), rounded_data.max() + 100, 100), edgecolor='black')
plt.title('Гистограмма округленных данных')
plt.xlabel('Значение (округлено до сотен)')
plt.ylabel('Частота')
plt.show()

#🟥 5. Создание DataFrame с добавлением отсортированных колонок
df = pd.DataFrame({'Исходный Series': series})
df['Отсортированный по возрастанию'] = df['Исходный Series'].sortvalues().resetindex(drop=True)
df['Отсортированный по убыванию'] = df['Исходный Series'].sortvalues(ascending=False).resetindex(drop=True)

#🟥 6. Визуализация отсортированных данных
plt.figure(figsize=(10, 4))
plt.plot(df['Отсортированный по возрастанию'], label='По возрастанию')
plt.plot(df['Отсортированный по убыванию'], label='По убыванию')
plt.title('Сравнение отсортированных данных')
plt.xlabel('Индекс')
plt.ylabel('Значение')
plt.legend()
plt.show()