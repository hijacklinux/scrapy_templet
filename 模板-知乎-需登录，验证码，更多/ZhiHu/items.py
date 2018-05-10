# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from ZhiHu.funcs.common import extract_num
from ZhiHu.settings import DATA_FORMAT,DATETIME_FORMAT
import datetime


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ZhihuQuestionItem(scrapy.Item):
    #知乎问题item
    zhihu_id        = scrapy.Field()
    topics          = scrapy.Field()
    url             = scrapy.Field()
    title           = scrapy.Field()
    content         = scrapy.Field()
    answer_num      = scrapy.Field()
    comments_num    = scrapy.Field()
    watch_user_num  = scrapy.Field()
    click_num       = scrapy.Field()
    crawl_time      = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎数据库question表的sql语句,on duplicate检查主键冲突，如果没有冲突就插入，有冲突的话就更新content等字段，免得sql错误
        insert_sql = '''
                    insert into zhihu_quesion(zhihu_id,topics,url,title,content,answer_num,comments_num,
                        watch_user_num,click_num,crawl_time) 
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
                    ON DUPLICATE KEY UPDATE 
                    content = values(content),comments_num = VALUES(comments_num),praise_num=VALUES(praise_num)
                     '''
        #现在开始处理item字段，item_loader获取到的都是list，需要转换成字符串或数值
        question_id     = int(''.join(self['question_id']) )   #转换方法1、（推荐）反正list里面只有一个元素，所以join后不会改变值
        topics       = ','.join(self['topics'])
        url          = self['url'][0]                    #转换方法2、容易数组越限
        title        = self['title'][0]
        content      = self['content'][0]
        answer_num   = extract_num(self['answer_num'][0])
        comments_num = extract_num(self['comments_num'][0])
        click_num    = extract_num(''.join(self['click_num']))
        crawl_time   = datetime.datetime.now().strftime(DATETIME_FORMAT)    #strftime把时间按照指定格式转换为字符串

        params =(question_id,topics,url,title,content,answer_num,comments_num,click_num,crawl_time)
        return insert_sql,params
        #这个函数目的在于以后piplines里面就不用改了，直接在这里面改，使用这个函数的返回值作为pipeline的参数

class ZhihuAnswerItem(scrapy.Item):
    #知乎回答item
    zhihu_id        = scrapy.Field()
    url             = scrapy.Field()
    question_id     = scrapy.Field()
    author_id       = scrapy.Field()
    content         = scrapy.Field()
    praise_num      = scrapy.Field()
    comments_num    = scrapy.Field()
    create_time     = scrapy.Field()
    update_time     = scrapy.Field()
    crawl_time      = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                     insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,praise_num,comments_num
                     create_time,update_time,crawl_time)
                     values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                     on duplicate key update xxxx...
                     '''
        create_time = datetime.datetime.fromtimestamp(self['create_time'])
        update_time = datetime.datetime.fromtimestamp(self['update_time'])
        params = (#因为这个item不是item_loader，所以不用转换
            self['zhihu_id'],self['url'],self['question_id'],self['author_id'],self['content'],self['praise_num'],
            self['comments_num'],create_time.strftime(DATETIME_FORMAT),update_time.strftime(DATETIME_FORMAT),self['crawl_time'].strftime(DATETIME_FORMAT)
        )   #这里面的create_time update_time是时间戳，需要转换成字符串
        return insert_sql,params