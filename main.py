import psycopg2

# параметры подключения
conn = psycopg2.connect(
    host="127.0.0.1",
    port="5432",
    database="Library",
    user="postgres",
    password="Mashinist132"
)

# создание курсора
cur = conn.cursor()

# выполнение SQL-запроса
cur.execute("SELECT * FROM orders")
rows = cur.fetchall()

# вывод результатов
for row in rows:
    print(row)

# закрытие курсора и соединения
cur.close()
conn.close()