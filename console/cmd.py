import mysql.connector
from decouple import config

DATABASE = config('DATABASE')
HOST = config('HOST')
USER = config('USER')
PASSWORD = config('PASSWORD')


class DatabaseConsole: 
    def __init__(self, host=HOST, user=USER, password=PASSWORD, database=DATABASE):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.selected = database
        self.cursor = self.connection.cursor()
        
    def list(self):
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()

        if len(tables) == 0:
            print("empty..") 
        
        # Выводим список таблиц
        for table in tables:
            print(table[0])
            
    def select(self, table_name):
        self.selected = table_name

    def execute_query(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def create_table(self, table_name, columns):
        columns_str = ', '.join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.execute_query(query)
        print(f"Table '{table_name}' created successfully.")

    def insert_data(self, table_name, values):
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(values.values()))
        print(f"Data inserted into '{table_name}' successfully.")

    def select_data(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def quit(self):
        if self.selected == DATABASE:
            print("exit..")
            self.connection.close()
            exit(0)
        else:
            self.selected = DATABASE
        
    def start(self):
        
        while True:
            try:
                user_input = input(f"{self.selected}: ")
            except KeyboardInterrupt:
                self.connection.close()
                exit()
                
            if not user_input:
                break

            try:
                command_parts = user_input.split(' ')
                command = command_parts[0]
                argument = ' '.join(command_parts[1:])
                
                if hasattr(self, command):
                    if argument == '':
                        getattr(self, command)()
                    else:
                        getattr(self, command)(argument)
                else:
                    print("Неверная команда.")
            except Exception as e:
                print(f"exit with error: {e}")
                self.connection.close()