from datetime import datetime
import json
import os

log_file_path_class = os.path.join('logs', "controller.log")
log_time_format = '%Y-%m-%d %H:%M:%S,%f'

    
import os
import shutil
import gzip
from datetime import datetime, timedelta
import threading
import time

class LogHandler:
    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.compress_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.schedule_compression()
        
    def json_log(log_file_path_class):
        with open(log_file_path_class, 'r', encoding='utf-8') as file:
            logs: list = [log.rstrip() for log in file]
        
        result = []
        
        for log in logs:
            time, name, level, msg = log.split(" - ")
            
            log_datetime = datetime.strptime(time, log_time_format)

            # Получение Unix-времени (timestamp)
            unix_timestamp = int(log_datetime.timestamp())

            
            result.append({
                "time": time,
                "timestamp": unix_timestamp,
                "name": name,
                "level": level,
                "msg": msg
            })
            
        return result

    def scan_and_compress_logs(self):
        log_files = [f for f in os.listdir(self.log_folder) if f.endswith(".json")]
        now = datetime.now()

        for log_file in log_files:
            log_path = os.path.join(self.log_folder, log_file)
            compressed_path = os.path.join(self.log_folder, f"{now.strftime('%Y-%m-%d')}_compressed.gz")
            
            with open(log_path, 'rb') as log_file:
                with gzip.open(compressed_path, 'wb') as compressed_file:
                    shutil.copyfileobj(log_file, compressed_file)
            os.remove(log_path)
            print(f"Logs compressed and renamed: {compressed_path}")

    def schedule_compression(self):
        while True:
            time_until_compress = self.compress_time - datetime.now()
            seconds_until_compress = time_until_compress.total_seconds()
            if seconds_until_compress < 0:
                seconds_until_compress += 86400
            time.sleep(seconds_until_compress)
            self.scan_and_compress_logs()
            self.compress_time += timedelta(days=1)

class Controller:
    def __init__(self):
        self.log_folder = "logs"  # Укажите ваш путь к папке с логами
        self.log_handler = LogHandler(self.log_folder)
        self.log_thread = threading.Thread(target=self.log_handler.schedule_compression, daemon=True)

    def start_monitoring(self):
        self.log_thread.start()

if __name__ == "__main__":
    controller = Controller()
    controller.start_monitoring()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    
if __name__ == '__main__':
    with open(os.path.join('logs', 'controller.json'), 'w', encoding='utf-8') as file:
        json.dump(json_log(), file, indent=4, ensure_ascii=False)