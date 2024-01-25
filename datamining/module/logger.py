from loguru import logger
import sys

class Logger:
    def __init__(self, class_name=None) -> None:
        self.class_name = class_name
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger_instance = logger
        if self.class_name:
            logger_instance = logger_instance.bind(class_name=self.class_name)
        logger_instance.add(sys.stderr, format="{time} - {extra[class_name]} - {message}")
        return logger_instance

    def main(self):
        self.logger.info('good_stuff')

class Bot(Logger):
    def __init__(self) -> None:
        super().__init__(class_name=__class__.__name__)

    def main(self):
        self.logger.info("Good")

class Setup(Logger):
    def __init__(self) -> None:
        super().__init__(class_name=__class__.__name__)
        
    def main(self):
        self.logger.error('Oshibka')

# Пример использования
x = Setup()
x.main()

bot = Bot()
bot.main()
