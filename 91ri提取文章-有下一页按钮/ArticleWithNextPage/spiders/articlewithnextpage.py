# -*- coding: utf-8 -*-
# 'Author = 'hijacklinux'
import scrapy
from scrapy.http import Request
from urllib import parse
from ArticleWithNextPage.items import ArticleItem,ArticleItemLoader
######根据实际更改

class ArticlewithnextpageSpider(scrapy.Spider):
    name = 'articlewithnextpage'
    allowed_domains = ['www.91ri.org']
    start_urls = ['http://www.91ri.org/category/anquan/safe',
                  'http://www.91ri.org/category/pentest/pentest-skills',
                  'http://www.91ri.org/tag/xss',
                  'http://www.91ri.org/tag/fuzz-bug',
                  'http://www.91ri.org/tag/neiwang-hacker',
                  'http://www.91ri.org/category/vulnerability/script-bugs',
                  'http://www.91ri.org/category/anquan/wlan',
                  'http://www.91ri.org/tag/social_engineering',
                  'http://www.91ri.org/tag/anquan-pdf']

    def parse(self, response):
        post_nodes = response.css('.posts.post-1.cf')
        ######根据实际更改

        for post_node in post_nodes:
            image_url = post_node.css('img::attr(data-src)').extract_first("")
            post_url = post_node.css('.right-col a::attr(href)').extract_first("")
            fenlei = post_node.css('.topic.left a::text').extract_first("")
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':parse.urljoin(response.url,image_url),'fenlei':fenlei},callback=self.parse_detail)

        next_page = response.css('.next.next_page a::attr(href)').extract_first()
        if next_page:
            yield Request(url=parse.urljoin(response.url,next_page),callback=self.parse)


    def parse_detail(self, response):
        front_image_url = response.meta.get('front_image_url', '')
        fenlei = response.meta.get('fenlei','')

        item_loader = ArticleItemLoader(item=ArticleItem(), response=response)

        item_loader.add_xpath('title','/html/body/div[2]/div[1]/div[1]/div/article/section[1]/header/h1/text()')
        item_loader.add_xpath('create_date','/html/body/div[2]/div[1]/div[1]/div/article/section[1]/header/div/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_md5', response.url)
        item_loader.add_value('front_image_url',[front_image_url])
        item_loader.add_value('fenlei',[fenlei])

        article_item = item_loader.load_item()
        yield article_item

