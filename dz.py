import telebot
import psycopg2


TOKEN = ''

bot = telebot.TeleBot(TOKEN)


conn_params = {
    'dbname': '',
    'user': 'postgres',
    'password': '',
    'host': '127.0.0.1',
    'port': 5432
}


conn = psycopg2.connect(**conn_params)
cursor = conn.cursor()


def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            phone VARCHAR(50) NOT NULL
        )
    ''')
    conn.commit()

create_tables()


user_states = {}
user_data = {}


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Привет! Давайте я помогу вам управлять данными клиентов.\n'
        'Команды:\n'
        '/add_client - добавить клиента\n'
        '/update_client - обновить клиента\n'
        '/delete_client - удалить клиента\n'
        '/find_client - найти клиента\n'
        '/add_phone - добавить телефон\n'
        '/delete_phone - удалить телефон'
    )
    user_states.pop(message.chat.id, None)
    user_data.pop(message.chat.id, None)



def add_client(first_name, last_name, email):
    try:
        cursor.execute('''
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (first_name, last_name, email))
        client_id = cursor.fetchone()[0]
        conn.commit()
        return client_id, None
    except Exception as e:
        conn.rollback()
        return None, str(e)

def add_phone(client_id, phone):
    try:
        cursor.execute('''
            INSERT INTO phones (client_id, phone)
            VALUES (%s, %s)
        ''', (client_id, phone))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)

def update_client(client_id, first_name=None, last_name=None, email=None):
    try:
        if first_name:
            cursor.execute('UPDATE clients SET first_name=%s WHERE id=%s', (first_name, client_id))
        if last_name:
            cursor.execute('UPDATE clients SET last_name=%s WHERE id=%s', (last_name, client_id))
        if email:
            cursor.execute('UPDATE clients SET email=%s WHERE id=%s', (email, client_id))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)

def delete_phone(phone):
    try:
        cursor.execute('DELETE FROM phones WHERE phone=%s', (phone,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)

def delete_client(client_id):
    try:
        cursor.execute('DELETE FROM clients WHERE id=%s', (client_id,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)

def find_client_by_name_or_email_or_phone(query):
    try:
        cursor.execute('''
            SELECT c.id, c.first_name, c.last_name, c.email, COALESCE(array_agg(p.phone) FILTER (WHERE p.phone IS NOT NULL), ARRAY[]::varchar[])
            FROM clients c
            LEFT JOIN phones p ON c.id = p.client_id
            WHERE c.first_name ILIKE %s OR c.last_name ILIKE %s OR c.email ILIKE %s OR p.phone ILIKE %s
            GROUP BY c.id
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return cursor.fetchall()
    except Exception:
        return []



@bot.message_handler(commands=['add_client'])
def handle_add_client(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Введите имя клиента:')
    user_states[chat_id] = 'adding_client_first_name'
    user_data[chat_id] = {}

@bot.message_handler(commands=['update_client'])
def handle_update_client(message):
    bot.send_message(message.chat.id, 'Введите ID клиента для обновления:')
    user_states[message.chat.id] = 'updating_client_id'
    user_data[message.chat.id] = {}

@bot.message_handler(commands=['delete_client'])
def handle_delete_client(message):
    bot.send_message(message.chat.id, 'Введите ID клиента для удаления:')
    user_states[message.chat.id] = 'deleting_client_id'
    user_data[message.chat.id] = {}

@bot.message_handler(commands=['find_client'])
def handle_find_client(message):
    bot.send_message(message.chat.id, 'Введите имя, фамилию, email или телефон для поиска:')
    user_states[message.chat.id] = 'finding_client'
    user_data[message.chat.id] = {}

@bot.message_handler(commands=['add_phone'])
def handle_add_phone_cmd(message):
    bot.send_message(message.chat.id, 'Введите ID клиента, которому хотите добавить телефон:')
    user_states[message.chat.id] = 'adding_phone_client_id'
    user_data[message.chat.id] = {}

@bot.message_handler(commands=['delete_phone'])
def handle_delete_phone_cmd(message):
    bot.send_message(message.chat.id, 'Введите телефон для удаления:')
    user_states[message.chat.id] = 'deleting_phone'
    user_data[message.chat.id] = {}



@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id)

    if state == 'adding_client_first_name':
        user_data[chat_id]['first_name'] = message.text.strip()
        bot.send_message(chat_id, 'Введите фамилию:')
        user_states[chat_id] = 'adding_client_last_name'

    elif state == 'adding_client_last_name':
        user_data[chat_id]['last_name'] = message.text.strip()
        bot.send_message(chat_id, 'Введите email:')
        user_states[chat_id] = 'adding_client_email'

    elif state == 'adding_client_email':
        email = message.text.strip()
        user_data[chat_id]['email'] = email
        # Добавляем клиента
        first_name = user_data[chat_id]['first_name']
        last_name = user_data[chat_id]['last_name']
        client_id, error = add_client(first_name, last_name, email)
        if client_id:
            bot.send_message(chat_id, f'Клиент добавлен с ID {client_id}. Теперь введите телефоны через запятую:')
            user_data[chat_id]['client_id'] = client_id
            user_states[chat_id] = 'adding_client_phones'
        else:
            bot.send_message(chat_id, f'Ошибка при добавлении клиента: {error}')
            user_states.pop(chat_id, None)
            user_data.pop(chat_id, None)

    elif state == 'adding_client_phones':
        phones_input = message.text
        phones = [p.strip() for p in phones_input.split(',') if p.strip()]
        client_id = user_data[chat_id]['client_id']
        errors = []
        for phone in phones:
            success, err = add_phone(client_id, phone)
            if not success:
                errors.append(err)
        if errors:
            bot.send_message(chat_id, f'Некоторые телефоны не добавлены: {errors}')
        else:
            bot.send_message(chat_id, 'Телефоны успешно добавлены.')
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    elif state == 'updating_client_id':
        try:
            client_id = int(message.text.strip())
            user_data[chat_id]['client_id'] = client_id
            bot.send_message(chat_id, 'Введите новое имя или оставьте пустым:')
            user_states[chat_id] = 'updating_first_name'
        except:
            bot.send_message(chat_id, 'Некорректный ID. Попробуйте снова.')
            user_states.pop(chat_id, None)
            user_data.pop(chat_id, None)

    elif state == 'updating_first_name':
        if message.text.strip():
            user_data[chat_id]['first_name'] = message.text.strip()
        else:
            user_data[chat_id]['first_name'] = None
        bot.send_message(chat_id, 'Введите новую фамилию или оставьте пустым:')
        user_states[chat_id] = 'updating_last_name'

    elif state == 'updating_last_name':
        if message.text.strip():
            user_data[chat_id]['last_name'] = message.text.strip()
        else:
            user_data[chat_id]['last_name'] = None
        bot.send_message(chat_id, 'Введите новый email или оставьте пустым:')
        user_states[chat_id] = 'updating_email'

    elif state == 'updating_email':
        if message.text.strip():
            user_data[chat_id]['email'] = message.text.strip()
        else:
            user_data[chat_id]['email'] = None
        data = user_data[chat_id]
        success, err = update_client(
            data['client_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email']
        )
        if success:
            bot.send_message(chat_id, 'Данные клиента обновлены.')
        else:
            bot.send_message(chat_id, f'Ошибка: {err}')
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    elif state == 'deleting_client_id':
        try:
            client_id = int(message.text.strip())
            success, err = delete_client(client_id)
            if success:
                bot.send_message(chat_id, 'Клиент удален.')
            else:
                bot.send_message(chat_id, f'Ошибка: {err}')
        except:
            bot.send_message(chat_id, 'Некорректный ID.')
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    elif state == 'finding_client':
        query = message.text.strip()
        results = find_client_by_name_or_email_or_phone(query)
        if results:
            response = ''
            for c in results:
                phones_str = ', '.join(c[4]) if c[4] else 'Нет телефонов'
                response += f'ID: {c[0]}, Имя: {c[1]}, Фамилия: {c[2]}, Email: {c[3]}, Телефоны: {phones_str}\n'
            bot.send_message(chat_id, response)
        else:
            bot.send_message(chat_id, 'Клиенты не найдены.')
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    elif state == 'adding_phone_client_id':
        try:
            client_id = int(message.text.strip())
            user_data[chat_id]['client_id'] = client_id
            bot.send_message(chat_id, 'Введите телефон для добавления:')
            user_states[chat_id] = 'adding_phone_number'
        except:
            bot.send_message(chat_id, 'Некорректный ID. Попробуйте снова.')
            user_states.pop(chat_id, None)
            user_data.pop(chat_id, None)

    elif state == 'adding_phone_number':
        phone = message.text.strip()
        client_id = user_data[chat_id]['client_id']
        success, err = add_phone(client_id, phone)
        if success:
            bot.send_message(chat_id, 'Телефон добавлен.')
        else:
            bot.send_message(chat_id, f'Ошибка: {err}')
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    elif state == 'deleting_phone':
        phone = message.text.strip()
        success, err = delete_phone(phone)
        if success:
            bot.send_message(chat_id, 'Телефон удален.')
        else:
            bot.send_message(chat_id, f'Ошибка: {err}')
        user_states.pop(chat_id, None)
        user_data.pop(chat_id, None)

    else:
        bot.send_message(
            chat_id,
            'Пожалуйста, используйте команду /start или одну из команд: /add_client, /update_client, /delete_client, /find_client, /add_phone, /delete_phone'
        )


bot.polling()