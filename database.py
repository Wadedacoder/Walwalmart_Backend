import mysql.connector
import json
import os

env_var = os.environ


class Database:
    def __init__(self):
        self.cnx = mysql.connector.connect(
            host=env_var["HOST"],
            user=env_var["USER"],
            password=env_var["PASSWORD"],
            database=env_var["DATABASE"],
            port=env_var["PORT"]
        )
        if(self.cnx):
            print("Connected to database ", env_var["DATABASE"])
        self.cursor = self.cnx.cursor(dictionary=True)

    def run_select_query(self, query, args=None) -> str:
        self.cursor.execute(query, args)
        result = self.cursor.fetchall()
        # print(result, type(result), "result")
        return json.dumps(result)

    def run_insert_query(self, query, args=None) -> bool:
        try:
            self.cursor.execute(query, args)
            self.cnx.commit()
            return True
        except:
            return False

    def run_update_query(self, query, args=None) -> bool:
        try:
            self.cursor.execute(query, args)
            self.cnx.commit()
            return True
        except:
            return False

    def run_delete_query(self, query, args=None) -> bool:
        try:
            self.cursor.execute(query, args)
            self.cnx.commit()
            return True
        except:
            return False