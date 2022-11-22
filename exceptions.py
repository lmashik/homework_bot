import json

import requests


class SendMessageToTelegramError(Exception):
	"""Ошибка отправки сообщения в телеграм."""
	pass


class JSONTypeError(json.JSONDecodeError):
	pass
