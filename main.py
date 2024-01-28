import asyncio
from console.cmd import DatabaseConsole
import os
from console.cmd import DatabaseConsole
from datamining.module.controller import Controller

if __name__ == "__main__":
    #scripts_folder = os.path.abspath("/home/lon8/python/projects/notickets/")
    scripts_folder = os.path.abspath("C:\\Users\\vladk\\Desktop\\notickets\\datamining\\scripts")
    config_path = os.path.abspath("config.json")
    log_file_path = "logs.log"
    
    controller = Controller(
                            scripts_folder=scripts_folder,
                            config_filename=config_path
                        )
    asyncio.run(controller.run_scripts())