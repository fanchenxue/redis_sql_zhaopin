# -*- coding: utf-8 -*-
import json
import redis  # pip install redis
import pymysql
import threading
def main():
    # 指定redis数据库信息
    rediscli = redis.StrictRedis(host='101.200.44.122', port = 6379, db = 0,password='123456')
    # 指定mysql数据库
    mysqlcli = pymysql.connect(host='127.0.0.1', user='root',passwd='', db='scrapy', charset='utf8')

    # 无限循环
    while True:
        source, data = rediscli.blpop(["tong:items"]) # 从redis里提取数据

        item = json.loads(data.decode('utf-8')) # 把 json转字典

        try:
            # 使用cursor()方法获取操作游标
            cur = mysqlcli.cursor()
            # 使用execute方法执行SQL INSERT语句
            sql = 'insert into gongzuo(jid,title,maxmoney,minmoney,location,degree,exp,crawled,url,spider) ' \
                  'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update title=values(title),maxmoney=VALUES(maxmoney),minmoney=values(minmoney)'
            data = (item["jid"], item["title"], item["maxmoney"], item["minmoney"], item["location"],item["degree"],item["exp"],item["crawled"],item["url"],item["spider"])
            cur.execute(sql,data)
            # 提交sql事务
            mysqlcli.commit()
            #关闭本次操作
            cur.close()
            print ("插入 %s" % item['title'])
        except pymysql.Error as e:
            mysqlcli.rollback()
            print ("插入错误",str(e))

if __name__ == '__main__':
    for i in range(1,10):
        t = threading.Thread()
        t.start()
        main()
        t.join()