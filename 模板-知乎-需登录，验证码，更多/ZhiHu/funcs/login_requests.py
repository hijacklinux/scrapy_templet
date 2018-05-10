import requests
#import cooklib python2
import http.cookiejar as cookielib      #python3
import re
import time
from PIL import Image

#目的在于requests登录，登录之后在下一次登陆时直接从文件里面读取cookie
agent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)'
header = {
    'HOST':'www.zhihu.com',
    'Referer':'https://www.zhihu.com',
    'User-agent':agent
}

session = requests.session() #这样就不需要每次都用requests建立session，用已有的session操作
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')#创建一个cookielib实例来保存cookie

try:
    session.cookies.load(ingore_discard = True)
except:
    print('cookie未能加载')

def is_login():
    #根据状态码判断是否为登录状态
    inbox_url = 'https://www.zhihu.com/inbox'
    response = session.get(inbox_url,headers = header,allow_redirects = False) #最后一个参数禁止跳转
    if response.status_code != 200:
        return False
    else:
        return True

def get_xsrf():
    #获取xsrf
    response = session.get('https://www.zhihu.com',headers = header)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"',response.text)
    if match_obj:
        return(match_obj.group(1))
    else:
        return ''

def get_index():
    response = session.get('https://www.zhihu.com', headers=header)

def get_captcha()
    t = str(int(time.time()*1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r={0}&type=login'.format(t)
    t = session.get(captcha_url,headers = header)
    #注意：不能用request，必须session，因为request会另外开一个session，这样返回的xsrf就不是之前获得的那个xsrf了
    with open('captcha.jpg','wb') as f:
        f.write(t.content)  #写如图片要用content，不能用text
        f.close()
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass
    captcha = input('请输入验证码')
    return captcha

def zhihu_login(account,password):
    #登录动作
    if re.match('^1\d{10}',account):
        print('手机号码登录')
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {'_xsrf':get_xsrf(),
                     'phone_num':account,
                     'password':password,
                     'captcha':get_captcha()}
    elif '@' in account:
        print('email登录')
        post_url = 'https://www.zhihu.com/login/email'
        post_data = {'_xsrf': get_xsrf(),
                     'email': account,
                     'password': password}
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()
