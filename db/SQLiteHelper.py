# coding:utf-8

from config import DB_CONFIG
from db.SqlHelper import SqlHelper
import MySQLdb

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class SqliteHelper(SqlHelper):
    tableName = 'proxy'

    def __init__(self):
        '''
        建立数据库的链接
        :return:
        '''
        self.database = MySQLdb.connect(host=DB_CONFIG['ip'],
                                        port=DB_CONFIG["port"],
                                        user=DB_CONFIG['user'],
                                        passwd=DB_CONFIG['passwd'],
                                        db=DB_CONFIG['db'],
                                        charset=DB_CONFIG["charset"]
                                        )

        self.cursor = self.database.cursor()
        # 创建表结构
        self.createTable()

    def compress(self):
        '''
        数据库进行压缩
        :return:
        '''
        self.database.execute('VACUUM')

    def createTable(self):
        self.cursor.execute("create TABLE IF NOT EXISTS %s (id INTEGER auto_increment PRIMARY KEY ,ip VARCHAR(16) NOT NULL,"
                            "port VARCHAR(16) NOT NULL ,types VARCHAR(16) NOT NULL ,protocol VARCHAR(16) NOT NULL DEFAULT 0,"
                            "country VARCHAR (20) NOT NULL,area VARCHAR (20) NOT NULL,updatetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,speed DECIMAL(6,2) NOT NULL DEFAULT 100.000)" % self.tableName)

        self.database.commit()

    def select(self, tableName, condition, count):
        '''

        :param tableName: 表名
        :param condition: 条件包含占位符
        :param value:  占位符所对应的值(主要是为了防注入)
        :return:
        '''

        command = 'SELECT DISTINCT ip,port FROM %s WHERE %s ORDER BY speed ASC %s ' % (tableName, condition, count)

        self.cursor.execute(command)
        result = self.cursor.fetchall()
        return result

    def selectAll(self):
        self.cursor.execute('SELECT DISTINCT ip,port FROM %s ORDER BY speed ASC ' % self.tableName)
        result = self.cursor.fetchall()
        return result

    def selectCount(self):
        self.cursor.execute('SELECT COUNT( DISTINCT ip) FROM %s' % self.tableName)
        count = self.cursor.fetchone()
        return count

    def selectOne(self, tableName, condition, value):
        '''

        :param tableName: 表名
        :param condition: 条件包含占位符
        :param value:  占位符所对应的值(主要是为了防注入)
        :return:
        '''
        self.cursor.execute('SELECT DISTINCT ip,port FROM %s WHERE %s ORDER BY speed ASC' % (tableName, condition),
                            value)
        result = self.cursor.fetchone()
        return result

    def update(self, tableName, condition, value):
        self.cursor.execute('UPDATE %s %s' % (tableName, condition), value)
        self.database.commit()

    def delete(self, tableName, condition):
        '''

        :param tableName: 表名
        :param condition: 条件
        :return:
        '''
        deleCommand = 'DELETE FROM %s WHERE %s' % (tableName, condition)

        self.cursor.execute(deleCommand)
        self.commit()

    def commit(self):
        self.database.commit()

    def insert(self, tableName, value):
        self.cursor.execute("ALTER TABLE %s MODIFY COLUMN country VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;" % tableName)
        self.cursor.execute("ALTER TABLE %s MODIFY COLUMN area VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;" % tableName)

        proxy = [value['ip'], value['port'], value['type'], value['protocol'], value['country'], value['area'],
                 value['speed']]

        self.cursor.execute("SET NAMES utf8")
        self.cursor.execute(
            "INSERT INTO proxy (ip,port,types,protocol,country,area,speed)VALUES (%s,%s,%s,%s,%s,%s,%s)" ,proxy)

    def batch_insert(self, tableName, values):

        for value in values:
            if value != None:
                self.insert(self.tableName, value)
        self.database.commit()

    def close(self):
        self.cursor.close()
        self.database.close()


if __name__ == "__main__":
    s = SqliteHelper()
    table = "proxy"
    value={'protocol': 0, 'area': u'\u6c5f\u82cf\u7701\u65e0\u9521\u5e02 \u7535\u4fe1', 'ip': '115.224.76.123', 'country': u'\u4e2d\u56fd', 'type': 0, 'port': 8118, 'speed': 0.56}

    s.insert(table,value)
    print s.selectAll()
