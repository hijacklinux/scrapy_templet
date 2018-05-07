# -*- coding: utf-8 -*-
# 'Author = 'hijacklinux'
import scrapy
from scrapy.loader.processors import MapCompose,TakeFirst
from scrapy.loader import ItemLoader
import hashlib
import re

class ArticlewithnextpageItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

#自定义函数
def get_md5(value):
    if isinstance(value,str):
        value = value.encode('utf-8')
    m = hashlib.md5()
    m.update(value)
    return m.hexdigest()

def do_nothing(value):
    return value

def date_convert(value):
    try:
        create_date = re.match(r' • (.*?) ',value).group(1)
    except Exception as e:
        create_date = value.strip()
    return create_date

class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(input_processor = MapCompose(date_convert))
    front_image_url = scrapy.Field(output_processor = MapCompose(do_nothing))
    front_image_path = scrapy.Field()
    url = scrapy.Field()
    url_md5 = scrapy.Field(input_processor = MapCompose(get_md5))
    fenlei = scrapy.Field(output_processor = MapCompose(do_nothing))

