from datamining.module.logger import Logger

class Bot(Logger):
    def __init__(self, log_file_path, logger_name):
        super().__init__(log_file_path, logger_name)