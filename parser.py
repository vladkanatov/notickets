from datamining.module.controller import Parser
from datamining.module.logger import logger

import json
from datetime import datetime


class Template(Parser):

    def __init__(self):
        super().__init__()

    async def main(self):

        for i in range(5):
            r = await self.session.get('https://api.ipify.org/')
            logger.debug(r.text)
            logger.debug("Hello")
