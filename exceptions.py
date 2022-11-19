class TelegramError(Exception):
	"""Ошибка отправки сообщения в телеграм."""
	pass


class MyKeyError(KeyError):
	"""Ошибка проверки ключей в словаре"""
	def __init__(self):
		super().__init__(
			'KeyError: В словаре нет запрашиваемого ключа.'
		)
