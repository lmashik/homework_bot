import json

import requests


class SendMessageToTelegramError(Exception):
	"""Ошибка отправки сообщения в телеграм."""
	pass


class JSONTypeError(Exception):
	pass


class APIRequestError(Exception):
	pass
