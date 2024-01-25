from loguru import Logger

class MyLogger(Logger):
    def __init__(self) -> None:
        super().__init__()
