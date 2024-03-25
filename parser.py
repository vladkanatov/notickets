from datamining.module.controller import Parser
from datamining.module.logger import logger


class ParserName(Parser):
    def __init__(self):
        super().__init__()

    async def main(self):
        logger.info('Hello, parser')

        # self.register_event()
