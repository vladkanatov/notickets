from loguru import logger
import sys

# Удалить старый логгер
logger.remove()

log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <blue>{extra[class_name]}</blue> | <cyan>{message}</cyan>"
logger_instance = logger # Общий логгер для всех экземпляров классов
logger_instance.add(sys.stderr, format=log_format)

class Logger:
      
    def __init__(self, class_name=None) -> None:
        self.logger_instance = logger_instance
        self.class_name = class_name
        self.logger = self.setup_logger()

    def setup_logger(self):
        if self.class_name:
            logger_instance = self.logger_instance.bind(class_name=self.class_name)
        return logger_instance

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

class Warn(Logger):
    def __init__(self) -> None:
        super().__init__(class_name=__class__.__name__)
        
    def main(self):
        self.logger.warning('Preduprezhdenie')

# Пример использования
x = Setup()
x.main()

w = Warn()
w.main()