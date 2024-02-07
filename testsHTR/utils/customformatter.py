import logging

#https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
class CustomFormatter(logging.Formatter):
	"""
	classe per formatar els logging

	Atributs
	--------
	logging.Formatter

	Mètodes
	-------
	format(record):
		formata el missatge
	"""
	
	bold = "\033[1m"
	blue = "\033[34m"
	green = "\u001b[32m"
	grey = "\x1b[38;20m"
	yellow = "\x1b[33;20m"
	red = "\x1b[31;20m"
	bold_red = "\x1b[31;1m"
	cyan = "\u001b[36m"
	reset = "\x1b[0m"
	#format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
	format = "%(name)s-%(levelname)s:l%(lineno)d - %(message)s"

	FORMATS = {
		logging.DEBUG: yellow + format + reset,
		logging.INFO: bold + blue + format + reset,
		logging.WARNING: yellow + format + reset,
		logging.ERROR: red + format + reset,
		logging.CRITICAL: bold_red + format + reset
	}

	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)
