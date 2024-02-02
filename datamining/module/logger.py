from loguru import logger
import sys
import inspect

# Remove the old logger
logger.remove()

log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <red>{function}:{line}</red> | <cyan>{message}</cyan>"
logger_instance = logger  # Common logger for all class instances
logger_instance.add(sys.stderr, format=log_format)


logger.info('good')