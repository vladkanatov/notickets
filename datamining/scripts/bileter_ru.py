from datetime import datetime
from datamining.module.controller import Parser

class Bileter(Parser):
    def __init__(self):
        super().__init__()
        
        self.delay = 5

    async def run(self):
        self.info("YES")
        self.register_event('','http', datetime.now())