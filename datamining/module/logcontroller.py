import json
import os
import re
import gzip
from datetime import datetime, timedelta
import threading
from .bot import Bot

log_file_path_class = os.path.join('logs', "controller.log")
log_time_format = '%Y-%m-%d %H:%M:%S,%f'

class LogController(Bot):
    def __init__(self, log_folder):
        self.log_folder = log_folder
        self.compress_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.schedule_compression()

    def parse_log_line(self, log_line):
        log_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\S+) - (.+)')
        match = log_pattern.match(log_line)
        if match:
            timestamp_str, name, level, msg = match.groups()
            timestamp = int(datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f").timestamp())
            return {
                "time": timestamp_str,
                "timestamp": timestamp,
                "name": name,
                "level": level,
                "msg": msg
            }
        else:
            return None

    async def serialize_and_compress_logs(self):
        log_files = [f for f in os.listdir(self.log_folder) if f.endswith(".log")]
        now = datetime.now()

        for log_file in log_files:
            log_path = os.path.join(self.log_folder, log_file)
            compressed_path = os.path.join(self.log_folder, f"{now.strftime('%Y-%m-%d')}_compressed.gz")

            with open(log_path, 'r') as log_file:
                logs = [self.parse_log_line(line) for line in log_file.readlines() if line.strip()]

            async with gzip.open(compressed_path, 'wb') as compressed_file:
                for log in logs:
                    log_json = json.dumps(log) + '\n'
                    compressed_file.write(log_json.encode('utf-8'))

            os.remove(log_path)
            self.info(f"Logs compressed and renamed: {compressed_path}")

    def schedule_compression(self):
        threading.Timer(self.time_until_midnight(), self.schedule_compression).start()
        self.serialize_and_compress_logs()

    def time_until_midnight(self):
        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return (midnight - datetime.now()).total_seconds()
