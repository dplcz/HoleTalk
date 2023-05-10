# -*-coding:utf-8-*-
from enum import Enum
import time
import sqlite3


class OperationStatus(Enum):
    Login_SUCCESS = 0
    Login_FAIL = 1
    Register_SUCCESS = 2
    ADD_SUCCESS = 3
    ADD_FAIL = 4
    SELECT_FAIL = 5
    DELETE_SUCCESS = 6
    DELETE_FAIL = 7


class AppDataModel:
    def __init__(self, memory=None):
        if memory:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect('data.db')

        self.conn.row_factory = self._dict_factory

        sql_user_table = '''CREATE TABLE user
                   (userid INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL ,
                    password TEXT NOT NULL ,
                    img_path TEXT);'''

        sql_server_table = '''CREATE TABLE server
                   (server_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL ,
                    address TEXT NOT NULL ,
                    password TEXT NOT NULL ,
                    img_path TEXT,
                    description TEXT,
                    user_id INTEGER,
                    last_connect_time timestamp,
                    foreign key(user_id) references user(userid));'''

        sql_history_message = '''CREATE TABLE history
                   (message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    send_info TEXT NOT NULL ,
                    message TEXT NOT NULL ,
                    send_time timestamp NOT NULL ,
                    user_id INTEGER,
                    server_id INTEGER,
                    send_me INTEGER default 0 not null ,
                    foreign key(server_id) references server(server_id) on delete cascade on update cascade,
                    foreign key(user_id) references user(userid));'''

        sql_list = ['PRAGMA FOREIGN_KEYS=ON;', sql_user_table, sql_server_table, sql_history_message]

        for sql in sql_list:
            try:
                self.conn.execute(sql)
            except sqlite3.OperationalError:
                continue

    @staticmethod
    def _dict_factory(cursor, row):
        d = {}
        for index, col in enumerate(cursor.description):
            if row[index] == 'NULL':
                d[col[0]] = None
            else:
                d[col[0]] = row[index]
        return d

    def check_user(self, username: str, password):
        if username.upper() == 'SERVER':
            return OperationStatus.Login_FAIL, None

        cur = self.conn.cursor()
        sql_check = "select * from user where username='{}'".format(username)
        cur.execute(sql_check)
        res = cur.fetchall()
        if len(res) == 1:
            res_user = res[0]
            if res_user['password'] == password:
                cur.close()
                return OperationStatus.Login_SUCCESS, res_user['userid']
            else:
                cur.close()
                return OperationStatus.Login_FAIL, None
        elif len(res) == 0:
            sql_insert = "insert into user values (NULL,'{}','{}',NULL)".format(username, password)
            cur.execute(sql_insert)
            self.conn.commit()
            sql_check = "select * from user where username='{}'".format(username)
            cur.execute(sql_check)
            res = cur.fetchall()[0]
            cur.close()
            return OperationStatus.Register_SUCCESS, res['userid']

    def _op_insert(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            return OperationStatus.ADD_SUCCESS
        except sqlite3.OperationalError:
            return OperationStatus.ADD_FAIL

    def _op_select(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            return result
        except sqlite3.OperationalError:
            return OperationStatus.SELECT_FAIL

    def _op_delete(self, sql):
        cur = self.conn.cursor()
        try:
            cur.execute(sql)
            self.conn.commit()
            cur.close()
            return OperationStatus.DELETE_SUCCESS
        except sqlite3.OperationalError:
            return OperationStatus.DELETE_FAIL

    def add_server(self, cur_user, name, address, password, img='NULL', desc='NULL'):
        sql_insert = "insert into server values (NULL,'{}','{}','{}','{}','{}',{},NULL)".format(name, address, password,
                                                                                                img,
                                                                                                desc, cur_user)
        return self._op_insert(sql_insert)

    def add_message(self, cur_user, cur_server, send_info, message, send_time=time.time(), send_me=0):
        sql_insert = "insert into history values (NULL,'{}','{}',{},{},{},{})".format(send_info, message,
                                                                                      int(send_time), cur_user,
                                                                                      cur_server, send_me)
        return self._op_insert(sql_insert)

    def get_server_list(self, cur_user):
        sql_select = "select * from server where user_id={}".format(cur_user)
        return self._op_select(sql_select)

    def get_history_list(self, cur_user, cur_server):
        sql_select = "select * from history where user_id={} and server_id={}".format(cur_user, cur_server)
        return self._op_select(sql_select)

    def delete_server(self, cur_user, cur_server):
        sql_delete = "delete from server where server_id={} and user_id={}".format(cur_server, cur_user)
        return self._op_delete(sql_delete)

    def delete_history(self, cur_user, cur_server):
        sql_delete = "delete from history where server_id={} and user_id={}".format(cur_server, cur_user)
        return self._op_delete(sql_delete)


if __name__ == '__main__':
    temp = AppDataModel()
    temp.check_user('dplcz6', '123456')
    temp.add_server(1, 'dplcz', 'dplcz.cn:8888', 'dplcz')
    temp.add_message(1, 1, 'server', 'aaaa')
    temp.get_server_list(1)
    temp.get_history_list(1, 1)
