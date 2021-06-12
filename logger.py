# logging.py

# conalarmd -- JT Ives
# Configures py stdlib logging module to write to systemd
# (stderr) w/ single line messages

import logging, os

class OneLineExc(logging.Formatter):
	""" subclasses loggin Formatter object to rewrite
	log messages as a single line """

	def formatException(self, exc_info):
		""" overrides formatException to return error msg in
		a text representable format """
		result = super().formatException(exc_info)
		return repr(result)

	def format(self, record):
		""" removes newline chars from error msg (if exists) """
		result = super().format(record)
		if record.exc_text:
			result = result.replace("\n", "")
		return result

# see logging module docs -- implements overridden formatter
handler = logging.StreamHandler()
formatter = OneLineExc(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
# logs any msg with level INFO or above to systemd (stderr)
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)
