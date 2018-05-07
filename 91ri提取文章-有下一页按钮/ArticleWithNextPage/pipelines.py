# -*- coding: utf-8 -*-
# 'Author = 'hijacklinux'
from scrapy.pipelines.images import ImagesPipeline
from openpyxl import Workbook
#获取封面图存储路径，不用改
class ArticleImagePipline(ImagesPipeline):
    def item_completed(self,results,item,info):
        for ok,value in results:
            image_file_path = value['path']
        item['front_image_path'] = image_file_path
        return item

class ArticlewithnextpagePipeline(object):
    def process_item(self, item, spider):
        return item

class ExcelExportPipeline(object):
    def __init__(self):
        self.spider = None
        self.count = 0

    def open_spider(self, spider):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['分类', '标题', '发布日期', '网址', '网址md5','封面网址','image_path'])

    def process_item(self, item, spider):
        line = [item['fenlei'][0], item['title'], item['create_date'], item['url'], item['url_md5'], item['front_image_url'][0],item['front_image_path']]
        self.ws.append(line)
        return item

    def close_spider(self, spider):
        print('ExcelPipline info:  items size: %s' % self.count)
        self.wb.save('91ri.xlsx')  # 保存xlsx文件
