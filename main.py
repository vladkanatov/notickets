import asyncio
from console.cmd import DatabaseConsole
import os
from console.cmd import DatabaseConsole
from datamining.module.controller import Controller

if __name__ == "__main__":
    scripts_folder = os.path.abspath("/home/lon8/python/projects/notickets/")
    config_path = os.path.abspath("config.json")
    log_file_path = "/home/lon8/python/projects/notickets/logs.log"
    
    controller = Controller(
                            log_file_path=log_file_path,
                            scripts_folder=scripts_folder,
                            config_filename=config_path
                        )
    asyncio.run(controller.run_scripts())