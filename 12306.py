#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from multiprocessing import Process
import os
#import psutil
from datetime import datetime
import time
import re
import urllib
import requests
from PIL import Image
import json
from json import loads, load
import getpass
from station_consts import STATIONS
from train_urls import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

reload(sys)
sys.setdefaultencoding('utf8')

configs = []
config = {}
username = ''
password = ''
fromStationCode = ''
toStationCode = ''
fromStationName = ''
toStationName = ''

# 由于12306官方验证码是验证正确验证码的坐标范围,我们取每个验证码中点的坐标(大约值)
captchaCoords = ['35,35','105,35','175,35','245,35','35,105','105,105','175,105','245,105']

class Tickets(object):
    def __init__(self):
        self.headers = {
            "Connection": "keep-alive",
            "Host":"kyfw.12306.cn",
            #"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
            # user-agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
            "User-Agent":"Mozilla/5.0 (Linux; Ubuntu 16.04; rv:57.0) Gecko/20100101 Firefox/57.0"
        }
        # 创建一个网络请求session实现登录验证
        self.session = requests.Session()
        self.pShowImage = None

    # 获取验证码图片
    def getImg(self):
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand";
        #https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5968060550787435
        #https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.7769218471372233
        response = self.session.get(url=url,headers=self.headers,verify=False)
        # 把验证码图片保存到本地
        with open('img.jpg','wb') as f:
            f.write(response.content)
        # 用pillow模块打开并解析验证码,这里是假的，自动解析以后学会了再实现
        try:
            #if self.pShowImage:
            #    self.pShowImage.terminate()
            #self.pShowImage = Process(target=self.showImg)
            #self.pShowImage.start()
            # p.join()
            self.im = Image.open('img.jpg')
            # 展示验证码图片，会调用系统自带的图片浏览器打开图片，线程阻塞
            self.im.show()
            # 关闭，只是代码关闭，实际上图片浏览器没有关闭，但是终端已经可以进行交互了(结束阻塞)
            self.im.close()
        except:
            print u'请输入验证码'

    def showImg(self):
        self.im = Image.open('img.jpg')
        # 展示验证码图片，会调用系统自带的图片浏览器打开图片，线程阻塞
        self.im.show()
        # 关闭，只是代码关闭，实际上图片浏览器没有关闭，但是终端已经可以进行交互了(结束阻塞)
        self.im.close()

    def inputPropt(self):
        print u'''
        #=======================================================================
        # 根据打开的图片识别验证码后手动输入，输入正确验证码对应的位置，例如：2,5
        # ---------------------------------------
        #         |         |         |
        #    1    |    2    |    3    |     4
        #         |         |         |
        # ---------------------------------------
        #         |         |         |
        #    5    |    6    |    7    |     8
        #         |         |         |
        # ---------------------------------------
        #=======================================================================
        '''
        return raw_input('请输入验证码位置，以","分割[例如2,5], 刷新验证码，输入r:')

    # 验证结果
    def checkCaptcha(self):
        text = self.inputPropt()
        while text == 'r':
            self.getImg()
            text = self.inputPropt()

        # 分割用户输入的验证码位置
        textList = text.split(',')
        captchaList = []
        for item in textList:
            print item
            captchaList.append(captchaCoords[int(item) - 1])
        # 正确验证码的坐标拼接成字符串，作为网络请求时的参数
        captchaStr = ','.join(captchaList)
        checkUrl = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {
            'login_site':'E',           #固定的
            'rand':'sjrand',            #固定的
            'answer':captchaStr    #验证码对应的坐标，两个为一组，跟选择顺序有关,有几个正确的，输入几个
        }
        # 发送验证
        response = self.session.post(url=checkUrl,data=data,headers=self.headers,verify=False)
        # 返回json格式的字符串，用json模块解析
        dic = loads(response.content)
        code = dic['result_code']
        # 取出验证结果，4：成功  5：验证失败  7：过期
        if str(code) == '4':
            return True
        else:
            print u"[*]检查验证码失败: %s" % response.content
            return False

    # 发送登录请求的方法
    def login(self):
        global username
        global password
        #userName = raw_input('Please input your userName:')
        # pwd = raw_input('Please input your password:')
        # 输入的内容不显示，但是会接收，一般用于密码隐藏
        #pwd = getpass.getpass('Please input your password:')
        data = {
            'username':username,
            'password':password,
            'appid':'otn'
        }
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/login/init"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"

              #"name": "Cookie",
              #"value": "_passport_session=4b36a156b4c34c02a66a9421bed6e7e54948; _passport_ct=0518eda7c9c14750b3d5c09cd789b916t1615; route=6f50b51faa11b987e576cdb301e545c4; BIGipServerotn=451412234.24610.0000; RAIL_EXPIRATION=1515698742622; RAIL_DEVICEID=o4z3H3hVVTNj8gz69EIeou7PWf98U0Dkfp1QG3tQaaX5Bx5-3argENHJReXBQ1IfwJxXFjqekDVuldP7MYtCt96zpXuormq3BuLckqiMYX4gFdrBSm5o7qL-HtxoBYu1PWIqoKo3x1gYzqcryfOURR2c9FVsgHWY; BIGipServerpassport=954728714.50215.0000; current_captcha_type=C; _jc_save_fromStation=%u6210%u90FD%2CCDW; _jc_save_toStation=%u6069%u65BD%2CESN; _jc_save_fromDate=2018-02-08; _jc_save_toDate=2018-01-10; _jc_save_wfdc_flag=dc; _jc_save_showIns=true; _jc_save_czxxcx_toStation=%u6069%u65BD%2CESN; _jc_save_czxxcx_fromDate=2018-02-09"
        response = self.session.post(url=loginUrl1,data=data,headers=headers,verify=False)
        print u"登录返回码: %s" % response.status_code

        result_code = "-1"
        try:
            dic = loads(response.content)
            result_code = dic['result_code']
            result_code = str(result_code)
            # {"result_message":"登录成功","result_code":0,"uamtk":"LecrN-dNoDcvRT_xkOcDXsjnPr2q2joCMDyAk6OtRnwkos2s0"}
            #if mes == u'登录成功':
            if "0" != result_code:
                print u"[*]登录失败1: %s" % response.content
        except BaseException, e:
            try:
                print u"[*]登录失败2: %s" % response.content
            except:
                pass
            print u"[*]登录异常: %s" % e
        finally:
            return result_code

    def authLogin(self):
        try:
            headers = self.headers
            headers['Host'] = 'kyfw.12306.cn'
            headers['Accept'] = """text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"""
            headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
            headers["Accept-Encoding"] = "gzip, deflate, br"
            headers["Referer"] = "https://kyfw.12306.cn/otn/login/init"
            headers['Content-Type'] = """application/x-www-form-urlencoded"""
            headers['DNT'] = '1'
            headers["Connection"] = "keep-alive"
            headers['Upgrade-Insecure-Requests'] = "1"
            #result = self.session.post(url=loginUrl2,data={"_json_att":""},headers=headers,verify=False)
            #print "POST userLogin result: %s" % result2.content
            print "POST userLogin end"

            headers = self.headers
            headers['Host'] = 'kyfw.12306.cn'
            headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
            headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
            headers["Accept-Encoding"] = "gzip, deflate, br"
            headers["Referer"] = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
            headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers['DNT'] = '1'
            headers["Connection"] = "keep-alive"
            result = self.session.post(url=uamtkUrl,data={"appid":"otn"},headers=headers,verify=False)
            # response: "text": "{\"result_message\":\"验证通过\",\"result_code\":0,\"apptk\":null,
            # \"newapptk\":\"_wZaQiNV_aMnAu4_LBlZBHefCkOBjVEt3yqzHzpg9Bsbcs1s0\"}"
            result_code = loads(result.content)['result_code']
            while 0 != result_code:
                print u"%s" % result.content
                print u"Get apptk failed: %s, try agian 2 seconds later" % result_code
                time.sleep(2)
                result = self.session.post(url=uamtkUrl,data={"appid":"otn"},headers=headers,verify=False)
                result_code = loads(result.content)['result_code']
            newapptk = loads(result.content)['newapptk']
            print u"POST uamtk end: %s" % newapptk

            headers = self.headers
            headers['Host'] = 'kyfw.12306.cn'
            headers['Accept'] =  "*/*"
            headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
            headers["Accept-Encoding"] = "gzip, deflate, br"
            headers["Referer"] = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
            headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers['DNT'] = '1'
            headers["Connection"] = "keep-alive"
            #"text": "tk=_wZaQiNV_aMnAu4_LBlZBHefCkOBjVEt3yqzHzpg9Bsbcs1s0"
            response = self.session.post(url=uamauthclientUrl,data={"tk":newapptk},headers=headers,verify=False)
            result_code = -1
            try:
                result_code = loads(response.content)['result_code']
            except BaseException, e:
                print u"post uamauthiclient response: %s" % response.content
                print u"Failed to get result code: %s" % e
            print u"POST uamauthclien end, result code: %s" % result_code
            print u"Cookies after POST uamauthclient: %s" % response.cookies

            #getUserLoginUrl
            headers = self.headers
            headers['Host'] = 'kyfw.12306.cn'
            headers['Accept'] =  "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
            headers["Accept-Encoding"] = "gzip, deflate, br"
            headers["Referer"] = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
            headers['DNT'] = '1'
            headers["Connection"] = "keep-alive"
            headers['Upgrade-Insecure-Requests'] = "1"
            result = self.session.post(url=getUserLoginUrl, data={"tk":newapptk},headers=headers,verify=False)
            print u"GET userlogin end"
            return True
        except BaseException, e:
            print u"Auth login failed: %s" % e
            return False

    def queryLeftTickets(self):
        global config
        global fromStationCode
        global toStationCode
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "*/*"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] = "https://kyfw.12306.cn/otn/leftTicket/init"
        headers["If-Modified-Since"] = "0"
        headers["Cache-Control"] = "no-cache"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        queryString = {
                'leftTicketDTO.train_date':config['depart_date'],
                'leftTicketDTO.from_station':fromStationCode,
                'leftTicketDTO.to_station':toStationCode,
                'purpose_codes':'ADULT'
                }
        arglist = ['leftTicketDTO.train_date=' + config['depart_date'],
                   'leftTicketDTO.from_station=' + fromStationCode,
                   'leftTicketDTO.to_station=' + toStationCode,
                   'purpose_codes=ADULT'
                    ]
        leftTicketUrl = getLeftTicketsUrl + "?" + '&'.join(arglist)
        response = {}
        content  = {}
        status   = False
        availableTrains = []
        req = requests.Request('GET', leftTicketUrl, headers=headers)
        prepped = self.session.prepare_request(req)

        try:
            # httpstatus: 200
            # messages:""
            # status: true or false
            # data: {}
            #response = self.session.get(url=getLeftTicketsUrl, params=queryString, headers=headers)
            response = self.session.send(prepped,
                          #stream=stream,
                          verify=False,
                          #proxies=proxies,
                          #cert=cert,
                          timeout=10
                          )
            #print "查询余票URL: %s" % response.request.url
            print "查询余票URL: %s" % prepped.url
            content  = loads(response.content)
            status   = content['status']
            candidateTrains = content['data']['result']
            if None != config['train_no'] and '' != config['train_no']:
                availableTrains = filter(self.trainFilterByNo, candidateTrains)
            else:
                availableTrains = candidateTrains
        except BaseException, e:
            print u"查询余票异常: %s" % e
        while len(availableTrains) < 1:
            try:
                if not status:
                    print u"%s" % response.content
                    print u"[*]查询余票失败, 2秒后重试"
                else:
                    print u"[*]没有余票, 2秒后重试"
                print "查询余票URL: %s" % prepped.url
                time.sleep(2)
                #response = self.session.get(url=getLeftTicketsUrl, params=queryString, headers=headers)
                response = self.session.send(prepped,
                                             #stream=stream,
                                             verify=False,
                                             #proxies=proxies,
                                             #cert=cert,
                                             timeout=10
                                             )
                content = loads(response.content)
                status = content['status']
                candidateTrains = content['data']['result']
                if None != config['train_no'] and '' != config['train_no']:
                    availableTrains = filter(self.trainFilterByNo, candidateTrains)
                else:
                    availableTrains = candidateTrains
            except KeyboardInterrupt, e:
                print u"[*]查询余票中断（%s）" % status
                return availableTrains
            except BaseException, e:
                pass
        return availableTrains

    def trainFilterByNo(self, train):
        global config
        fields = train.split('|')
        trainNo = fields[3]
        return trainNo == config['train_no']

    def buyTickets(self, tickets):
        # '''"cO1H6YX8YGo7g1x%2BwEh2svRjS4MPkj1D7zexIoQEpmpOBn2FhqiWNh9geqO9CqQlhjPUUCCsJRFW%0AtWfgD7tDyEOOK1ujyqffD9TmIqlmOjThaNQ%2BRqFWiUf8XXBR39y5RxueqBDazxq%2B4jTCpZ7jYuEN%0ARQ3iW4jskblQx%2B7EpNQVpzAaVa5Mc9NIB1zz6ka4mVor8uFqrkE72AUYykyKqLL5qbtIp5gQI3yi%0AkQBHFhcYD7F4iRx493WnrFxX2azZ
        #|预订|76000D22440C|
        #D2244|ICW   |FZS  |ICW   |ESN  |06:43 |11:42 |04:59 |Y     |OajMKAzDQz7wEFpkCGrY6GWmEeyx5zQsanidEVx0ZetfcelR
        #3    4始发   5终点  6出发  7到达  8发时   9到时  10历时  11当日  12

        #|20180116 |3 |W1 |01 |07 |0 |0 |  |  |  |  |  |  |有 |   |  |    |无  |20  |   |    |O0M0O0 |OMO  |0",'''
        #13        14 15  16  17  18 19 20 21 22 23 24 25 26  27  28 29   30   31  32   33   34      35

        # "|23:00-06:00系统维护时间|76000D22440C|D2244|ICW|FZS|ICW|ESN..."
        print u"%3s | %5s | %10s | %10s | %10s | %10s | %10s | %10s" % \
              (u"序号", u"车次", u"出发 - 到达", u"发时 - 到时", u"历时", u"特等座", u"一等座", u"二等座")
        idx = 0
        self.checkUser()
        for ticket in tickets:
            fields  = ticket.split('|')
            seceret = urllib.unquote(fields[0])
            trainNo = fields[2]
            leftTicketStr = fields[12]
            idx = idx + 1
            print u"%3s | %5s | %10s | %10s | %10s | %10s | %10s | %10s" % \
                  (idx, fields[3], \
                   STATIONS[fields[6]]['name'] + '-' + STATIONS[fields[7]]['name'], \
                   fields[8] + ' - ' + fields[9], fields[10], \
                   fields[31], fields[31], fields[30])
            print u"[*]创建订单请求..."
            self.submitOrder(seceret, STATIONS[fields[6]]['name'], STATIONS[fields[7]]['name'])
            (repeatSubmitToken, keyCheckIsChange) = self.initDc()
            #self.getPassengers(repeatSubmitToken)
            print u"[*]检查订单信息..."
            if not self.checkOrderInfo(repeatSubmitToken):
                continue

            print u"[*]查询余票详情..."
            withSeatCount, noSeatCount = self.getQueueCount(trainNo, fields[3], fields[15], fromStationCode, toStationCode, \
                                                            leftTicketStr, repeatSubmitToken)
            print u"余票：　有座－%s张, 无座－%s张" % (withSeatCount, noSeatCount)
            print u"[*]提交订单..."
            if self.confirmOrder(repeatSubmitToken, keyCheckIsChange, leftTicketStr):
                print u"[*]查询订单号..."
                if self.queryOrderState(repeatSubmitToken):
                    return True
                else:
                    print u"[*]查询订单号失败，尝试购买下一趟列车..."
                    continue

    def checkUser(self):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "*/*"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/leftTicket/init"
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["If-Modified-Since"] = "0"
        headers["Cache-Control"] = "no-cache"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"

        # json:
        # _json_att
        # resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"flag":true},"messages":[],"validateMessages":{}}
        response = self.session.post(url=checkUserUrl, data={'_json_att':''}, headers=headers, verify=False)
        print u"[*]检查用户结果: %s" % response.content

    def submitOrder(self, secretStr, fromName, toName):
        global config
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "*/*"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/leftTicket/init?random=" + str(int(time.time()))
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        print u"submitOrder %s - %s" % (fromName, toName)
        data = {
            'secretStr': secretStr,
            'train_date': config['depart_date'],
            #'back_train_date': '2018-01-10',
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': fromName,
            'query_to_station_name': toName,
            'undefined': ''
        }
        # resp ok: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":"N",
        #   "messages":[],"validateMessages":{}}
        # resp nok: {"validateMessagesShowId":"_validatorMessage","status":false,"httpstatus":200,
        #   "messages":["车票信息已过期，请重新查询最新车票信息"],"validateMessages":{}}
        response = {}
        status = False
        dict = {}
        try:
            response = self.session.post(url=submitOrderUrl, data=data, headers=headers, verify=False)
            status = loads(response.content)['status']
        except BaseException, e:
            pass
        while not status:
            print u"[*]创建订单请求出错: %s, 2 秒后重试" % response.content
            time.sleep(2)
            try:
                response = self.session.post(url=submitOrderUrl, data=data, headers=headers, verify=False)
                status = loads(response.content)['status']
            except KeyboardInterrupt, e:
                print u"[*]创建订单中断（%s）" % status
                return dict['status']
            except BaseException, e:
                pass
        return status

    def initDc(self):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = """text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"""
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/leftTicket/init?random=" + str(int(time.time()))
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        headers['Upgrade-Insecure-Requests'] = "1"
        #
        # json _json_att
        result = self.session.post(url=initDcUrl, data={'_json_att':''}, headers=headers, verify=False)
        #print "initdc result: %s" % result.content
        # var globalRepeatSubmitToken = '7100381b00696bc94607092cbeb28167';
        repeatSubmitToken = ""
        m = re.search("var globalRepeatSubmitToken = '(.*?)';", result.content)
        if m:
            repeatSubmitToken = m.group(1)
        print u"repeat submit token: %s" % repeatSubmitToken
        keyCheckIsChange = ""
        # 'key_check_isChange':'A0B67C6693D70DCE0533B140D45E53299C95C802D05CEAE752CE896B',
        m = re.search("'key_check_isChange'\s*:\s*'(.*?)'.*?,", result.content)
        if m:
            keyCheckIsChange = m.group(1)
        print u"key_check_isChange: %s" % keyCheckIsChange
        #              'leftTicketStr':'ByyR5GeiUJIZgGro5zy%2BL2ayYMYQiHVq7Nnep10Qkz5wTxuUjhAoprybxjo%3D',
        leftTicketStr = ""
        return (repeatSubmitToken, keyCheckIsChange)

    def getPassengers(self, repeatSubmitToken):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "*/*"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        #  89 #{"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"isExist":true,"exMsg":"","two_isOpenClick":["93","95","97","99"],
        # "other_isOpenClick":["91","93","98","99","95","97"],
        # "normal_passengers":[{"code":"13","passenger_name":"","sex_code":"M","sex_name":"男",
        #                       "born_date":"1900-00-00 00:00:00","country_code":"CN",
        #                       "passenger_id_type_code":"1","passenger_id_type_name":"二代身份证",
        #                       "passenger_id_no":"xxxxxxxx","passenger_type":"1","passenger_flag":"0",
        #                       "passenger_type_name":"成人","mobile_no":"13888888882","phone_no":"","email":"","address":"",
        #                       "postalcode":"","first_letter":"","recordCount":"13","total_times":"99","index_id":"0"},
        response = self.session.post(url=getPassengersUrl, data=data, headers=headers, verify=False)

    def getPassengerTicketStr(self):
        global config
        #   {"name":"name", "gender":"female", "id":"id_num", "phone_num":"phone_num", "seat_type":"一等座"}
        passengerTicketList = []
        oldPassengerTicketList = []
        childrenTicketsCount = 0
        for passenger in config["passengers"]:
            seatType = ""
            if u"成人" == passenger['ticket_type']:
                if u"一等座" == passenger['seat_type']:
                    seatType = "M,0,1"
                elif u"二等座" == passenger['seat_type']:
                    seatType = "O,0,1"
            elif u"儿童" == passenger['ticket_type']:
                childrenTicketsCount += 1
                if u"一等座" == passenger['seat_type']:
                    seatType = "M,0,2"
                elif u"二等座" == passenger['seat_type']:
                    seatType = "O,0,2"
            else:
                seatType = "O,0,1"
            passengerTicketList.append(",".join([seatType, passenger['name'], "1", \
                                                passenger['id'], passenger['phone_num'], "N"]))
            if u"成人" == passenger['ticket_type']:
                oldPassengerTicketList.append(",".join([passenger['name'], "1", passenger["id"], "1_"]))
        self.passengerTicketStr = "_".join(passengerTicketList)
        self.oldPassengerTicketStr = "".join(oldPassengerTicketList) + "_+" * childrenTicketsCount
        #print "ticket str: %s" % self.passengerTicketStr
        #print "old ticker str: %s" % self.oldPassengerTicketStr

    def checkOrderInfo(self, repeatSubmitToken):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        # cancel_flag	2
        # bed_level_order_num	000000000000000000000000000000
        # (一等座 女成人，二等座 男成人，儿童票)
        # passengerTicketStr	M,0,1,name,1,id_num,phone_num,N_O,0,1,name,1,id_num,phone_num,N_O,0,2,name,1,id_num,phone_num,N
        # count of '_+' equal to children tickets count
        # oldPassengerStr	name,1,id_num,1_name,1,id_num,1__+
        # tour_flag	dc
        # randCode
        # whatsSelect	1
        # _json_att
        # REPEAT_SUBMIT_TOKEN	ec44e1cf799034bca551530b2f131728
        data = {
            'cancel_flag': 2,
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': self.passengerTicketStr,
            'oldPassengerStr': self.oldPassengerTicketStr,
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': 1,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        # resp:
        # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"ifShowPassCode":"N","canChooseBeds":"N","canChooseSeats":"Y","choose_Seats":"OM",
        # "isCanChooseMid":"N","ifShowPassCodeTime":"1","submitStatus":true,"smokeStr":""},"messages":[],"validateMessages":{}}
        #
        # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"errMsg":"系统繁忙，请稍后重试！","submitStatus":false},"messages":[],"validateMessages":{}}

        # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"checkSeatNum":true,"errMsg":"您选择了1位乘车人，但本次列车一等座仅剩0张。","submitStatus":false},"messages":[],"validateMessages":{}}
        response = {}
        submitStatus = False
        try:
            response = self.session.post(url=checkOrderInfoUrl, data=data, headers=headers, verify=False)
            submitStatus = loads(response.content)['data']['submitStatus']
        except Excepation, e:
            pass
            #print "[*]检查订单信息异常: %s" % e
        while not submitStatus:
            try:
                if re.match(r"0张", response.content):
                    print u"\n[*]余票不足: %s, 2秒后重试" % response.content
                else:
                    print u"[*]检查订单信息失败: %s, 2秒后重试" % response.content
                print u"\n[*]Press Ctrl + C to stop\n"
                time.sleep(2)
                response = self.session.post(url=checkOrderInfoUrl, data=data, headers=headers, verify=False)
                submitStatus = loads(response.content)['data']['submitStatus']
            except KeyboardInterrupt, e:
                print u"[*]中断检查（%s）" % submitStatus
                return submitStatus
            except Excepation, e:
                pass
        return submitStatus

    def getQueueCount(self, trainNo, trainCode, trainLocation, fromStationCode, toStationCode, leftTicketStr, repeatSubmitToken):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        dt = datetime.strptime(config['depart_date'], "%Y-%m-%d")
        format = "%a+%b+%d+%Y+%H:%M:%S+GMT+0800+(CST)"
        data = {
            'train_date': dt.strftime(format),
            #'train_date': 'Thu+Feb+08+2018+00:00:00+GMT+0800+(CST)',
            'train_no': trainNo,
            'stationTrainCode': trainCode,
            'seatType': 'O',
            'fromStationCodeTelecode': fromStationCode,
            'toStationCodeTelecode': toStationCode,
            'leftTicket': leftTicketStr,
            'purpose_codes': '00',
            'train_location': trainLocation,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        req = requests.Request('POST', getQueueCountUrl, headers=headers)
        #req = requests.Request('POST', getQueueCountUrl, data=data, headers=headers)
        prepped = self.session.prepare_request(req)
        #prepped.body = json.dumps(data)
        body = "_json_att=&stationTrainCode=" + trainCode + "&train_no=" + trainNo + "&leftTicket=" + leftTicketStr + \
                "&train_location=W1&fromStationCodeTelecode=" + fromStationCode + "&seatType=O&toStationCodeTelecode=" + toStationCode + \
                "&REPEAT_SUBMIT_TOKEN=" + repeatSubmitToken + \
                "&train_date=" + dt.strftime("%a+%b+%d+%Y") + "+00%3A00%3A00+GMT%2B0800+(CST)&purpose_codes=00"""
        prepped.body = body
        print u"查询余票详情请求数据: %s" % prepped.body

        # resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"count":"0","ticket":"27,144","op_2":"false","countT":"0","op_1":"false"},"messages":[],"validateMessages":{}}
        ticketsCount = (0,0)
        response = None
        dict = {}
        status = False
        try:
            #response = self.session.send(prepped,
            #                            #stream=stream,
            #                            verify=False,
            #                            #proxies=proxies,
            #                            #cert=cert,
            #                            timeout=10
            #                            )
            response = self.session.post(url=getQueueCountUrl, data=body, headers=headers, verify=False)
            dict = loads(response.content)
            status = dict['status']
        except BaseException, e:
            print u"[*]查询余票详情失败: %s" % response
        while not status:
            try:
                print u"[*]查询余票详情失败: %s, 2秒后重试" % response.content
                time.sleep(2)
                response = self.session.post(url=getQueueCountUrl, data=body, headers=headers, verify=False)
                #response = self.session.send(prepped,
                #                             #stream=stream,
                #                             verify=False,
                #                             #proxies=proxies,
                #                             #cert=cert,
                #                             timeout=10
                #                             )
                dict = loads(response.content)
                status = dict['status']
            except KeyboardInterrupt, e:
                print u"[*]查询余票详情中断（%s" % ticketsCount
                break
            except BaseException, e:
                pass
        try:
            data = dict['data']
            tickets = data['ticket'].split(',')
            ticketsCount = (tickets[0], tickets[1])
        except BaseException, e:
            print u"get queue count failed, error: %s" % e
        return ticketsCount

    def confirmOrder(self, repeatSubmitToken, keyCheckIsChange, leftTicketStr):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        data = {
            'passengerTicketStr':self.passengerTicketStr,
            'oldPassengerStr':self.oldPassengerTicketStr,
            'randCode':"",
            'purpose_codes': '00',
            'key_check_isChange': keyCheckIsChange,
            'leftTicketStr': leftTicketStr,
            'train_location': "W1",
            'choose_seats': "",
            #'choose_seats': "1F", ###
            'seatDetailType': '000',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        # resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        #        "data":{"submitStatus":true},"messages":[],"validateMessages":{}}
        response = ""
        submitStatus = False
        try:
            response = self.session.post(url=confirmOrderUrl, data=data, headers=headers, verify=False)
            print u"[*]提交订单结果：%s" % response.content
            submitStatus = loads(response.content)['data']['submitStatus']
        except BaseException, e:
            print u"[*]提交订单结果：%s" % response.content
            print u"[*]提交订单出错：%s" % e
        return submitStatus

    def queryOrderState(self, repeatSubmitToken):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = "application/json, text/javascript, */*; q=0.01"
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        #"url": "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?
        # random=1515663658830&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=581c6aabe3f8085d048eba6373dee66f",
        queryString = {
                  "random":str(int(time.time())),
                  "tourFlag":"dc",
                  "_json_att":"",
                  "REPEAT_SUBMIT_TOKEN":repeatSubmitToken
                  }
        #"text": "{\"validateMessagesShowId\":\"_validatorMessage\",\"status\":true,\"httpstatus\":200,
        # \"data\":{\"queryOrderWaitTimeStatus\":true,\"count\":0,\"waitTime\":4,\"requestId\":1234567890123456786,
        #           \"waitCount\":1,\"tourFlag\":\"dc\",\"orderId\":null},\"messages\":[],\"validateMessages\":{}}"

        #"text": "{\"validateMessagesShowId\":\"_validatorMessage\",\"status\":true,\"httpstatus\":200,
        # \"data\":{\"queryOrderWaitTimeStatus\":true,\"count\":0,\"waitTime\":-1,\"requestId\":1234567890123456786,
        #           \"waitCount\":0,\"tourFlag\":\"dc\",\"orderId\":\"E123456789\"},\"messages\":[],\"validateMessages\":{}}"
        response = {}
        orderId = None
        try:
            response = self.session.get(url=queryOrderStateUrl, params=queryString, headers=headers)
            orderId = loads(response.content)['data']['orderId']
        except BaseException, e:
            pass
        while not orderId:
            try:
                print u"[*]查询订单状态..."
                time.sleep(1)
                response = self.session.get(url=queryOrderStateUrl, params=queryString, headers=headers)
                orderId = loads(response.content)['data']['orderId']
            except KeyboardInterrupt, e:
                print u"[*]中断查询（%s）" % response.content
                return orderId
            except BaseException, e:
                pass
        print u"[*]订单 [%s] 创建成功!" % orderId
        return orderId

    def logout(self):
        headers = self.headers
        headers['Host'] = 'kyfw.12306.cn'
        headers['Accept'] = """text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"""
        headers["Accept-Language"] = "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Referer"] =  "https://kyfw.12306.cn/otn/leftTicket/init"
        headers['Content-Type'] = """application/x-www-form-urlencoded; charset=UTF-8"""
        headers['DNT'] = '1'
        headers["Connection"] = "keep-alive"
        headers['Upgrade-Insecure-Requests'] = "1"
        print u"Logging out..."
        response = self.session.get(url=logoutUrl, headers=headers)


def parseConfigs():
    global configs
    global username
    global password
    global fromStationCode
    global toStationCode
    global fromStationName
    global toStationName
    configFile = './tickets.config'
    with open(configFile, 'r') as f:
        configs = load(f)
        #print u"configs: %s" % configs
    try:
        if len(configs) < 1:
            print u"[*]请配置购票信息."
            sys.exit(-1)
    except BaseException, e:
        print u"配置文件错误: %s" % e
        sys.exit(-1)
    credFile = './credential.config'
    with open(credFile, 'r') as f:
        creds = load(f)
        username = creds['user_name']
        password = creds['password']

def loopCheckCaptcha(tickets):
    chek = False
    #只有验证成功后才能执行登录操作
    while not chek:
        chek = tickets.checkCaptcha()
        if chek:
            print u'验证通过!'
        else:
            print u'验证失败，请重新验证!'

def loopLogin(tickets):
    loginResult = "-1"
    try:
        loginResult = tickets.login()
    except:
        pass
    while "0" != loginResult:
        # try:
        #     tickets.logout()
        # except BaseException, e:
        #     pass
        if "5" == loginResult:
            loopCheckCaptcha(tickets)
        else:
            print u'登录失败，try again 2 seconds later!'

        time.sleep(2)
        loginResult = False
        try:
            loginResult = tickets.login()
        except:
            pass

if __name__ == '__main__':
    parseConfigs()
    tickets = Tickets()
    tickets.getImg()
    print u"[*]处理验证码...\n"
    loopCheckCaptcha(tickets)
    if tickets.pShowImage:
        tickets.pShowImage.terminate()

    print u"[*]登录...\n"
    loopLogin(tickets)
    print u'\n[*]登录成功!\n'

    while not tickets.authLogin():
        print u"[*]验证登录失败, 2秒后重试..."
        time.sleep(2)

    print u'\n[*]开始购票...\n'
    for (idx, config) in enumerate(configs):
        fromStationCode = STATIONS[config['from_station']]['code']
        toStationCode   = STATIONS[config['to_station']]['code']
        fromStationName = STATIONS[config['from_station']]['name']
        toStationName   = STATIONS[config['to_station']]['name']
        print u"[*] %s: 尝试购买 [%s] 日从 [%s] 到 [%s] 的车票..." % (idx, config['depart_date'], fromStationName, toStationName)
        if len(config['passengers']) < 1:
            continue
        tickets.getPassengerTicketStr()
        leftTickets = tickets.queryLeftTickets()
        if len(leftTickets) < 1:
            print u"[*]购买 [%s] 日从 [%s] 到 [%s] 到车票失败，尝试下一趟列车..." % (config['depart_date'], fromStationName, toStationName)
            continue
        result = False
        try:
            result = tickets.buyTickets(leftTickets)
        except BaseException, e:
            print u"[*] %s 购票失败: %s, 尝试下一车次\n" % (idx, e)
        if result:
            print u"[*]购票成功，请登录12306网站付款。"
            break

    tickets.logout()
