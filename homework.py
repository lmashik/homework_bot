import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict, List, Union

import requests
import telegram.error
from dotenv import load_dotenv
from telegram import Bot

from exceptions import TelegramError, MyKeyError

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
    ]
)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: Bot, message: str) -> TelegramError:
    """Отправляет пользователю сообщения от лица бота."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        raise TelegramError(f'Ошибка отправки сообщения: {error}.')
    else:
        logging.info(f'Сообщение "{message}" успешно отправлено.')


def get_api_answer(current_timestamp: float) -> Dict:
    """Обращается к эндпоинту API-сервиса Практикум.Домашка"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if response.status_code != HTTPStatus.OK:
        raise requests.RequestException

    try:
        return response.json()
    except requests.JSONDecodeError as error:
        raise error


def check_response(response: Dict) -> List:
    """Проверяет ответа API сервиса Практикум.Домашка"""
    try:
        if not isinstance(response, Dict):
            raise(
                f'Пришедшие данные не являются словарем. '
            )
        else:
            homeworks_reviews = response.get('homeworks')
    except MyKeyError:
        raise
    else:
        if not isinstance(homeworks_reviews, List):
            raise Exception('Объект не является списком')
        return homeworks_reviews


def parse_status(homework: Dict) -> str:
    """Возвращает статус конкретной домашней работы."""
    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
    except MyKeyError:
        raise
    else:
        verdict = HOMEWORK_STATUSES[homework_status]

        return (
            f'Изменился статус проверки работы "{homework_name}". '
            f'{verdict}'
        )


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения."""
    if (
            not TELEGRAM_TOKEN or
            not TELEGRAM_CHAT_ID or
            not PRACTICUM_TOKEN
    ):
        return False
    else:
        return True


def main() -> None:
    """Основная логика работы бота."""

    main_message = 'Сбой в работе программы: '
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    prev_message = ''

    if not check_tokens():
        logging.critical(
            'Не хватает переменных окружения. '
            'Программа принудительно остановлена.'
        )
        sys.exit(
            'Не хватает переменных окружения. '
            'Программа принудительно остановлена.'
        )

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks_reviews = check_response(response)
            if homeworks_reviews:
                last_review = parse_status(homeworks_reviews[0])
                send_message(bot, last_review)
            else:
                logging.debug('Новые статусы отсутствуют.')

            current_timestamp = int(time.time())

        except TelegramError as error:
            logging.error(f'{main_message} {error}')
        except Exception as error:
            error_message = f'{main_message} {error}'
            if error_message != prev_message:
                send_message(bot, error_message)
                logging.info(f'Отправлено сообщение: {error_message}')
                prev_message = error_message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
