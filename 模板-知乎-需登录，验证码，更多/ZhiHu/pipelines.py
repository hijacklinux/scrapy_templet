# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import MYSQLdb
import MYSQLdb.cursors

class ZhihuPipeline(object):
    def process_item(self, item, spider):
        return item


#可以实现异步化操作，twisted只是提供一个异步容器
class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
       dbparms = dict(
                                host         = settings['MYSQL_HOST']  ,  #读取settings.py中的值
                                db           = settings['MYSQL_DBNAME'],
                                user         = settings['MYSQL_USER'],
                                passwd       = settings['MYSQL_PASSWORD'],
                                charset      = 'utf-8',
                                cursorclass  = MYSQLdb.cursors.DictCursor,
                                use_unicode  = True
                            )
        dbpool = adbapi.ConnectionPool('MySQLdb',  **dbparms)
        return cls(dbpool)

    def process_item(self,item,spider):
            #使用twisted把mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self,failure,item,spider):
        #处理异步插入异常,这个很重要，可以看到哪里出错
        print(failure)

    def do_insert(self,cursor,item):
        #执行具体sql语句
        #根据不同的item构建不同的sql语句

        insert_sql,params = item.get_insert_sql()
        self.cursor.execute(insert_sql,params)