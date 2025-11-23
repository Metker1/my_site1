import psycopg2
conn = psycopg2.connect(dbname='test_data',user='postgres',password='Mashinist132',host='127.0.0.1')
cursor = conn.cursor()

# Cоздание БД

# cursor.execute('CREATE TABLE IF NOT EXISTS people '
#                '(id SERIAL PRIMARY KEY, '
#                'name VARCHAR(50), '
#                'age INTEGER)')

# cursor.execute("INSERT INTO people (name,age) VALUES ('Иван',40)")

# bob = ('Кирилл',30)
# cursor.execute("INSERT INTO people (name,age) "
#                "VALUES (%s,%s)",bob)

# people = [('Влад',29),('Илья',39),('Владимир',30)]
#
# # Множественное добавление
# cursor.executemany('INSERT INTO people(name,age) '
#                    'VALUES (%s,%s)',people)

# Получение данных из БД
# cursor.execute('SELECT * FROM people')
# print(cursor.fetchall())

# cursor.execute('SELECT * FROM people')
# for person in cursor.fetchall():
#     print(f'{person[1]} - {person[2]}')


# cursor.execute('SELECT * FROM people')
# # Извлекаем первые 3 строки
# print(cursor.fetchmany(3))

# Извлекаем 1 строку
# cursor.execute('SELECT * FROM people')
# print(cursor.fetchone())

# cursor.execute('SELECT name,age FROM people '
#                'WHERE id=2')
# name,age = cursor.fetchone()
# print(name,age)


# Изменение данных
# cursor.execute("UPDATE people "
#                "SET name = 'Алексей' "
#                "WHERE name='Кирилл'")

# cursor.execute("UPDATE people SET name = %s "
#                "WHERE name=%s",("Иван","Степан"))

# подтверждаем транзакцию
conn.commit()
print('База данных успешно создана!')

cursor.close()
conn.close()