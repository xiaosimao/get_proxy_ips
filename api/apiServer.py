# coding:utf-8
'''
定义几个关键字，count type,protocol,country,area,
'''
import urllib
from config import API_PORT
from db.SQLiteHelper import SqliteHelper

__author__ = 'Xaxdus'

import BaseHTTPServer
import json
import urlparse
import logging

logger = logging.getLogger('api')


# keylist=['count', 'types','protocol','country','area']
# BaseHTTPRequestHandler  web处理器类
class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    BaseHTTPRequestHandler其中的实例变量有：
    1）client_address 包含关联的客户端地址（host, port）
    2）command 包含请求类型（eg: get ）
    3）path 包含的请求路径
    4）request_version 包含请求版本的字符串（eg: 'HTTP/1.0'）
    5）headers
    6）rfile 输入流
    7）wfile 包含写到客户端响应的输出流

    BaseHTTPRequestHandler的类变量有：
    1）server_version 指定服务器软件版本
    2）sys_version Python系统版本
    3）error_message_format
    4）protocol_version 响应中使用的HTTP协议版本

    BaseHTTPRequestHandler部分操作
    1）handle()
    2）send_error(code[, message]) 发送并记录一个完整的错误回复到客户端
    3）send_response(code[, message]) 发送一个响应头并记录已接收的请求
    4）send_header(keyword, value) 编写一个指定的HTTP头到输出流
    5）version_string() 饭后服务器软件的版本字符串
    """

    def do_GET(self):
        """
        """
        dict = {}

        parsed_path = urlparse.urlparse(self.path)

        try:
            query = urllib.unquote(parsed_path.query)
            logger.info("query %s" % query)
            if query.find('&') != -1:
                params = query.split('&')
                for param in params:
                    dict[param.split('=')[0]] = param.split('=')[1]
            else:
                dict[query.split('=')[0]] = query.split('=')[1]

            sqlHelper = SqliteHelper()
            # 处理删除代理的请求
            if dict.has_key('delete'):
                condition = "ip='" + dict['ip'] + "' AND port=" + dict['port']
                sqlHelper.delete(SqliteHelper.tableName, condition)
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Success delete proxy: " + dict['ip'] + ":" + dict['port'])
            else:
                str_count = ''
                conditions = []
                for key in dict:
                    if key == 'count':
                        str_count = 'LIMIT 0,%s' % dict[key]
                    if key == 'country' or key == 'area':
                        conditions.append(key + " LIKE '" + dict[key] + "%'")
                    elif key == 'types' or key == 'protocol' or key == 'country' or key == 'area':
                        conditions.append(key + "=" + dict[key])
                if len(conditions) > 1:
                    conditions = ' AND '.join(conditions)
                else:
                    conditions = conditions[0]

                result = sqlHelper.select(sqlHelper.tableName, conditions, str_count)
                # print type(result)
                # for r in  result:
                #     print r

                data = [{'ip': item[0], 'port': item[1]} for item in result]

                data = json.dumps(data)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
        except Exception, e:
            logger.warning(str(e))
            self.send_response(404)


if __name__ == '__main__':
    server = BaseHTTPServer.HTTPServer(('0.0.0.0', API_PORT), WebRequestHandler)
    server.serve_forever()  # 设置一直监听请求
