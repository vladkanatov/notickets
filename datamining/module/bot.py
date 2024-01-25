from logger import Logger

class Bot(Logger):
    def __init__(self):
        super().__init__()
        self.info('Привет')

bot = Bot()
