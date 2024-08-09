import asyncio
from datamining.controller import Controller

if __name__ == "__main__":
    controller = Controller()
    asyncio.run(controller.run())
