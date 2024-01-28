from .logger import Logger

class Bot(Logger):
    def __init__(self):
        super().__init__(class_name=__class__.__name__)

    def main(self):
        self.logger.info('Good')
        
if __name__ == '__main__':
    x = Bot()
    x.main()