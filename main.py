import asyncio
import os
from datamining.module.controller import Controller

if __name__ == "__main__":
    controller = Controller()
    asyncio.run(controller.run())
