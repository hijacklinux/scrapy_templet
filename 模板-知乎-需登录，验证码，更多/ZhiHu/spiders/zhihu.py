# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
import time
from scrapy.loader import ItemLoader
from ZhiHu.items import ZhihuAnswerItem,ZhihuQuestionItem
from PIL import Image
try:
    import urlparse as parse    #python2
except:
    from urllib import parse    #python3


class ZhihuSpider(scrapy.Spider):
    name                = 'zhihu'
    allowed_domains     = ['www.zhihu.com']
    start_urls          = ['http://www.zhihu.com/']
    start_answer_url    = 'https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}'
    #这个url是进入问题页面，鼠标下滚，而出现的url，之所以写上它是因为，如果不写上，那么就没有一个入口来获取‘更多’answer的url
    #换句话说，这个url就可以理解为，获取answer的请求url（通过控制question_id、limit、offset）
    #把question_id、limit、offset格式化{0}{1}{2}
    headers = {
        'HOST'      : 'www.zhihu.com',
        'Referer'   : 'https://www.zhihu.com',
        'User-agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)'
    }
    #这个不是入口，下面的start_request才是最先进行的
    def parse(self, response):#其实这个函数应该用在任何页面，但是为了逻辑清晰，先不写在question页面了
        '''
        #深度优先策略，提取出html页面中的所有url，并跟踪这些url进一步爬取
        如果提取的url中格式为/question/xxx就下载之后进入parse_question函数
        '''
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        #提取出的结果中有的是'javascript:;',因此需要过滤掉
        all_urls = filter(lambda x:True if x.startswith('https') else False,all_urls)
        #返回True的都会放在列表里，False的都会被过滤掉
        for url in all_urls:
            """
            需要提取两种情况
            1、https://www.zhihu.com/question/21696230/answer/385712570
            中的https://www.zhihu.com/question/21696230
            2、https://www.zhihu.com/question/21696230
            所以需要（/|$）
            """
            match_obj = re.match('(.*zhihu.com/question/(\d+))(/|$).*',url)
            if match_obj:
                #如果是问题url，则交给parse_question处理
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url,headers = self.headers,meta = {'question_id':question_id},callback = self.parse_question)
                ##############
                # break 调试的时候break掉，免得不停请求
                # 回调 ↓
            else:#如果不是问题url，那么跟进这个url，继续提取
                #############
                #pass    #调试的时候先pass，否则会不停地向知乎发请求
                yield scrapy.Request(url,headers = self.headers,callback = self.parse)

    def parse_question(self,response):
        #处理question页面，从页面中提取出具体的question item
        question_id = response.meta.get('question_id','')

        item_loader = ItemLoader(item = ZhihuQuestionItem(),response = response)
        item_loader.add_css('title','h1.QuestionHeader-title::text')
        item_loader.add_css('content','.QuestionHeader-detail')
        item_loader.add_value('url',response.url)
        item_loader.add_value('question_id',[question_id])
        item_loader.add_css('answer_num','.List-headerText span::text')
        item_loader.add_css('comments_num','.QuestionHeader-actions button::text')
        item_loader.add_css('watch_user_num','.NumberBoard-value::text')    #这里能够提取出两个数值，先放着，到时候详细处理
        item_loader.add_css('topics','.QuestionHeader-topics .Popover div::text')
        #多个主题，空格表示后代，'>'表示只能是儿子，孙子不行
        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id,20,0),callback=self.parse_answer,headers = self.headers)
        yield question_item     #yield question_item后，就会提交到pipelines处理
        #############如果我们要调试answer的item，那么yield question_item就可以注释掉，免得进入pipelines
        # 上上行的yield回调  ↓

    def parse_answer(self,response):
        #处理answer页面的json数据
        ans_json        = json.loads(response.text)
        is_end          = ans_json['paging']['is_end']
        totals_answer   = ans_json['paging']['totals']
        next_url        = ans_json['paging']['next']

        #提取answer具体字段item
        for answer in ans_json['data']:
            answer_item                 = ZhihuAnswerItem()
            answer_item['zhihu_id']     = answer['id']
            answer_item['url']          = answer['url']
            answer_item['question_id']  = answer['question']['id']
            answer_item['author_id']    = answer['author']['id'] if 'id' in answer['author'] else None
            #有的是匿名回复，没有id
            answer_item['content']      = answer['content'] if 'content' in answer else None
            answer_item['praise_num']   = answer['voteup_count']
            answer_item['comments_num'] = answer['comment_count']
            answer_item['create_time']  = answer['created_time']
            answer_item['update_time']  = answer['updated_time']
            answer_item['crawl_time']   = datetime.datetime.now()#爬取时间
            yield answer_item   #交给pipelines进一步处理

        if not is_end:
            yield scrapy.Request(next_url,headers = self.headers,callback=self.parse_answer)









    #知乎必须登录才能看到，而start_requests是scrapy的一个入口，所以需要重写start_requests
    #这里才是入口
    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/signup?next=%2F',headers = self.headers,callback=self.login)]
        #获取一个页面来获得一个xsrf,返回页面为500,就说明没传headers
        #回调 ↓
    def login(self,response):
        response_text = response.text
        match_obj     = re.match('.*name="_xsrf" value="(.*?)"', response_text,re.DOTALL)
        #正则表达式只找第一行的，所以需要加上re.DOTALL
        xsrf          = ''
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf: #必须获取到xsrf，如果获取不到，也就没必要登录了

            post_data   = {'_xsrf'    : xsrf,
                           'phone_num': '13567899876',
                           'password' : 'password',
                           'captcha'  :''}
            t           = str(int(time.time()*1000))  #获取一个随机数
            captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)

            yield scrapy.Request(
                captcha_url,
                headers = self.headers,
                meta    ={'post_data':post_data},
                callback= self.login_after_captcha )
            #这样就解决了scrapy没办法提取session的问题了，yield可以保证在同一个cookie下，直接yield回调到 ↓
        # 回调 ↓

    def login_after_captcha(self,response):
        #保存图片
        with open('captcha.jpg','wb') as f:
            f.write(response.body)  #scrapy中图片的值就不是content了，是body
            f.close()
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            pass

        captcha             = input('请输入验证码：\n')
        post_url            = 'https://www.zhihu.com/login/phone_num'
        post_data           = response.meta.get('post_data',{})
        post_data['captcha']=captcha
        return [scrapy.FormRequest( #登录请求
                url      = post_url,    #需要post提交到的url
                formdata = post_data,   #post数据
                headers  = self.headers,
                callback = self.check_login
            )]
        #回调 ↓

    def check_login(self,response):
        #验证服务器返回数据判断是否成功,scrapy会默认把cookie存储，不需要手动存储
        text_json = json.loads(response.text)
        if 'msg' in text_json and text_json['msg'] == '登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url,dont_filter=True,headers = self.headers)
                #这个不用变,不指定callback,就默认回调parse


