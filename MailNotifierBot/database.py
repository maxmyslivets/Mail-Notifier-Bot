import os
import sqlite3

from MailNotifierBot.logger import logger
from config import DATABASE


def create_database():
    try:
        # Проверка, что базы данных не существует
        if not os.path.exists(DATABASE):
            logger.debug(f"Create SQLite database in {DATABASE}")
            # Установка соединения с базой данных
            with sqlite3.connect(DATABASE) as conn:
                # Создание курсора
                cur = conn.cursor()

                # Создание таблицы сообщений
                cur.execute('CREATE TABLE messages (id_message TEXT, PRIMARY KEY (id_message))')

                # Сохранение изменений
                conn.commit()
    except sqlite3.Error as error:
        logger.error(f"Ошибка при работе с SQLite: {error}")


def check_read_messages(id_message: str) -> bool:
    try:
        logger.debug(f"Check id message in database")
        # Установка соединения с базой данных
        with sqlite3.connect(DATABASE) as conn:
            # Создание курсора
            cur = conn.cursor()

            # Поиск сообщения в базе данных
            cur.execute('SELECT id_message FROM messages WHERE id_message = ?', (id_message,))
            result = cur.fetchone()

            # Если сообщение найдено, возвращается True, иначе - False
            return result is not None
    except sqlite3.Error as e:
        logger.error(f"Error {e.args[0]} occurred while checking message {id_message}.")
        return False


def set_read_messages(id_message: str) -> None:
    try:
        logger.debug(f"Setting id message in database")
        # Установка соединения с базой данных
        with sqlite3.connect(DATABASE) as conn:
            # Создание курсора
            cur = conn.cursor()

            # Добавление сообщения в базу данных
            cur.execute('INSERT INTO messages (id_message) VALUES (?)', (id_message,))

            # Сохранение изменений
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error {e.args[0]} occurred while setting message {id_message} as read.")
