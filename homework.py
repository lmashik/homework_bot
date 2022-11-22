import json
import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Dict, List

import requests
import telegram.error
from dotenv import load_dotenv
from telegram import Bot

from exceptions import JSONTypeError

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
RETRY_PERIOD = 600

TOKENS = {
    'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
    'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    'PRACTICUM_TOKEN': PRACTICUM_TOKEN
}

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения."""
    tokens_are_available = True
    unavailable_tokens_list = [
        token for token, value in globals().items()
        if (token in TOKENS and value is None)
    ]
    if unavailable_tokens_list:
        tokens_are_available = False
        unavailable_tokens = ', '.join(unavailable_tokens_list)

        logging.critical(
            f'Отсутствует обязательная(-ые) переменная(-ые) '
            f'окружения: {unavailable_tokens}.'
        )

    return tokens_are_available


def send_message(bot: Bot, message: str) -> None:
    """Отправляет пользователю сообщения от лица бота."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        logging.error(
            f'Ошибка отправки сообщения: {error}.'
        )
    else:
        logging.debug(f'Сообщение "{message}" успешно отправлено.')


def get_api_answer(timestamp: float) -> Dict:
    """Обращается к эндпоинту API-сервиса Практикум.Домашка."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Ошибка соединения.')
    except Exception as error:
        raise ConnectionError(
            'Не удалось получить корректный ответ от API-сервиса.'
        ) from error
    try:
        return response.json()
    except json.JSONDecodeError:
        raise JSONTypeError('Ответ - невалидный json.')


def check_response(response: Dict) -> List:
    """Проверяет ответа API сервиса Практикум.Домашка."""
    if not isinstance(response, Dict):
        raise TypeError('Пришедшие данные не являются словарем.')

    if 'homeworks' not in response:
        raise KeyError('В словаре ответа нет ключа homeworks.')

    homeworks_reviews = response['homeworks']

    if not isinstance(homeworks_reviews, List):
        raise TypeError('Значение по ключу homeworks - не список.')

    return homeworks_reviews


def parse_status(homework: Dict) -> str:
    """Возвращает статус конкретной домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('Ключа homework_name нет в словаре homework.')

    if 'status' not in homework:
        raise KeyError('Ключа status нет в словаре homework.')

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(
            'Ключа homework_status нет в словаре HOMEWORK_VERDICTS.'
        )

    verdict = HOMEWORK_VERDICTS[homework_status]

    return (
        f'Изменился статус проверки работы "{homework_name}". '
        f'{verdict}'
    )


def main() -> None:
    """Основная логика работы бота."""
    main_message = 'Сбой в работе программы: '
    prev_message = ''

    if not check_tokens():
        sys.exit('Программа принудительно остановлена.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks_reviews = check_response(response)
            if homeworks_reviews:
                last_review = parse_status(homeworks_reviews[0])
                send_message(bot, last_review)
            else:
                logging.debug('Новые статусы отсутствуют.')

            timestamp = int(time.time())

        except Exception as error:
            error_message = f'{main_message} {error}'
            logging.exception(error_message)
            if error_message != prev_message:
                send_message(bot, error_message)
                prev_message = error_message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
