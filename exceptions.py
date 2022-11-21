import requests


class SendMessageToTelegramError(Exception):
	"""Ошибка отправки сообщения в телеграм."""
	pass


class APIRequestError(requests.RequestException):
	"""Ошибка запроса к API-сервису."""
	pass


