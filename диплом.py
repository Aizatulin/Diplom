# -*- coding: utf-8 -*-
"""Диплом.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15PSL8mebszsu6mvjE03S9A1Xz7HzpICR
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as st

#Загрузите файл HR.csv в pandas dataframe
df = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/DIPLOM/HR.csv')

df

# Для возможности анализа зарплаты переведем значения в порядковые
#df['salary2'] = df['salary']
df['salary'] = df['salary'].replace('low', 0)
df['salary'] = df['salary'].replace('medium', 1)
df['salary'] = df['salary'].replace('high', 2)
df

"""2.Рассчитайте основные статистики для переменных(среднее,медиана,мода,мин/макс,сред.отклонение)"""

df.describe()

"""3. Рассчитайте и визуализировать корреляционную матрицу для количественных переменных.Определите две самые скоррелированные и две наименее скоррелированные переменные"""

print (len(df['satisfaction_level'].unique()),'\n')
print (len(df['last_evaluation'].unique()),'\n')
print (len(df['average_montly_hours'].unique()))

# Все параметры дискретные (кроме "департамента" и зарплаты), три из них  - колличественные. Для них посчитаем корреляцию по Пирсону (посмотреть), а для всех по Спирмену и Кенделл.

df[['satisfaction_level', 'last_evaluation', 'average_montly_hours']].corr()

df.corr(method='spearman')

"""Наиболее скоррелированные - average_montly_hours и number_project,

наименее: time_spend_company и salary.
"""

sns.set(rc={'figure.figsize':(11.7,8.27)})
sns.heatmap(df.corr(method='kendall'), annot=True)

"""Результат такой же!

Наиболее скоррелированные - average_montly_hours и number_project,

наименее: time_spend_company и salary.

4. Рассчитайте сколько сотрудников работает в каждом департаменте.
"""

df.groupby('department').count()['salary'].sort_values()

"""5. Показать распределение сотрудников по зарплатам."""

s = df.groupby('salary').count()['left']
#plt.hist(df.groupby('salary').count()['left'])
s.plot(kind='bar')

"""(Везде Salary 0-low, 1-medium, 2-high)

6. Показать распределение сотрудников по зарплатам в каждом департаменте по отдельности
"""

df.pivot_table(index = 'salary', columns = 'department', values = 'left', aggfunc = 'count').head()

#len(df.loc[(df.salary==0)])# & (df.department=='accounting')])

"""7. Проверить гипотезу, что сотрудники с высоким окладом проводят на работе больше времени, чем сотрудники с низким окладом"""

s_low = df[df.salary==0]['average_montly_hours']
s_low.describe()

s_high = df[df.salary==2]['average_montly_hours']
s_high.describe()

# H0 - среднее время работы выборки сотрудников с высоким и низким окладом одинаковы
# H1 - среднее время работы выборки сотрудников с низким окладом выше чем с высоким
alpha = 0.05
result = st.ttest_ind(s_low, s_high, equal_var=False)
print(result)

if (result.pvalue < alpha):
    print('Отвергаем нулевую гипотезу')
else:
    print('Не отвергаем нулевую гипотезу, время работы не зависит от оклада.')

# Проверим, найдем корреляцию низкой и высокой зарплаты со временем работы выборки сотрудник не со средней зарплатой.
ss =  df[df.salary != 1][['average_montly_hours', 'salary']]
ss.corr(method='spearman')

"""Подтвердился результат, корреляция отсутствует.

8. Рассчитать следующие показатели среди уволившихся и неуволившихся сотрудников (по отдельности)
- Доля сотрудников с повышением за последние 5 лет
"""

t1 = round(100*len(df[(df.left == 0) & (df.promotion_last_5years == 1)]) / len(df[(df.left == 0)]),1)
t2 = round(100*len(df[(df.left == 1) & (df.promotion_last_5years == 1)]) / len(df[(df.left == 1)]),1)
print (f"Доля сотрудников с повышением: действующих {t1}% и уволенных {t2}% (ко всем действующим и ко всем уволеным соответственно).")

"""- Средняя степень удовлетворенности"""

print ("Действующие: {:2.2f}, уволенные: {:2.2f}".format(df[df.left==0]['satisfaction_level'].mean(), df.groupby('left')['satisfaction_level'].mean()[1])) # разные способы специально

"""- Среднее количество проектов"""

q = df.groupby('left')['number_project'].mean()
q.index=(['Действующие','Уволенные'])
q

"""9. Разделить данные на тестовую и обучающую выборки. 
Построить модель LDA, предсказывающую уволился ли сотрудник на основе имеющихся факторов (кроме department и salary).
Оценить качество модели на тестовой выборки
"""

df2 = df.copy()
df2.drop(['department', 'salary', 'left'], axis=1, inplace=True)
df2

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(df2, df['left'], test_size=0.30, random_state=42)
y_test

X_test

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

lda = LinearDiscriminantAnalysis()
lda.fit(X_train, y_train)

# делаем прогноз на тестовой выборке
lda.predict(X_test)

# смотрим разницу факта и прогноза

result = pd.DataFrame(y_test)
result['Result'] = lda.predict(X_test)
result

len(result[result.left != result.Result])

# расчет точности - отношение верных прогнозов к общему количеству позиций

from sklearn.metrics import accuracy_score

"Успешных предсказаний {:.2%}".format(accuracy_score(result['left'], result['Result']))

"""Из интереса смотрим, как изменится результат если добавить Salary."""

df2 = df.copy()
df2.drop(['department', 'left'], axis=1, inplace=True)
df2

X_train, X_test, y_train, y_test = train_test_split(df2, df['left'], test_size=0.30, random_state=42)
y_test

lda = LinearDiscriminantAnalysis()
lda.fit(X_train, y_train)

# делаем прогноз на тестовой выборке
lda.predict(X_test)

# смотрим разницу факта и прогноза

result = pd.DataFrame(y_test)
result['Result'] = lda.predict(X_test)
result

# расчет точности - отношение верных прогнозов к общему количеству позиций

from sklearn.metrics import accuracy_score

"Успешных предсказаний {:.2%}".format(accuracy_score(result['left'], result['Result']))

"""У модели выросла результативность на ~1.5%."""