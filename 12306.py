#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import requests
import time
from PIL import Image
import json
from json import loads, load
import getpass
from station_consts import STATIONS
from train_urls import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

configs = {}
username = ''
password = ''
fromStation = ''
toStation = ''

# 由于12306官方验证码是验证正确验证码的坐标范围,我们取每个验证码中点的坐标(大约值)
captchaCoords = ['35,35','105,35','175,35','245,35','35,105','105,105','175,105','245,105']

class LoginTic(object):
    def __init__(self):
        self.headers = {
            "Connection": "keep-alive",
            "Host":"kyfw.12306.cn",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        # 创建一个网络请求session实现登录验证
        self.session = requests.session()

    # 获取验证码图片
    def getImg(self):
        url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand";
        response = self.session.get(url=url,headers=self.headers,verify=False)
        # 把验证码图片保存到本地
        with open('img.jpg','wb') as f:
            f.write(response.content)
        # 用pillow模块打开并解析验证码,这里是假的，自动解析以后学会了再实现
        try:
            self.im = Image.open('img.jpg')
            # 展示验证码图片，会调用系统自带的图片浏览器打开图片，线程阻塞
            self.im.show()
            # 关闭，只是代码关闭，实际上图片浏览器没有关闭，但是终端已经可以进行交互了(结束阻塞)
            self.im.close()
        except:
            print u'请输入验证码'

    def inputPropt(self):
        print '''
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
            login.getImg()
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
        cont = self.session.post(url=checkUrl,data=data,headers=self.headers,verify=False)
        # 返回json格式的字符串，用json模块解析
        dic = loads(cont.content)
        code = dic['result_code']
        # 取出验证结果，4：成功  5：验证失败  7：过期
        if str(code) == '4':
            return True
        else:
            return False

    # 发送登录请求的方法
    def loginTo(self):
        global username
        global password
        #userName = raw_input('Please input your userName:')
        # pwd = raw_input('Please input your password:')
        # 输入的内容不显示，但是会接收，一般用于密码隐藏
        #pwd = getpass.getpass('Please input your password:')
        loginUrl = "https://kyfw.12306.cn/passport/web/login"
        data = {
            'username':username,
            'password':password,
            'appid':'otn'
        }
        loginHeaders = self.headers
        loginHeaders['Refer'] = 'https://kyfw.12306.cn/otn/login/init'
        result = self.session.post(url=loginUrl,data=data,headers=self.headers,verify=False)
        print "Login response code: %s" % result.status_code
        #print "Login response: %s" % result.content
        dic = loads(result.content)
        mes = dic['result_message']
        # 结果的编码方式是Unicode编码，所以对比的时候字符串前面加u,或者mes.encode('utf-8') == '登录成功'进行判断，否则报错
        if mes == u'登录成功':
            return True
        else:
            return dic['result_code']

    def queryLeftTickets(self):
        #leftTicketUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=2018-01-16&leftTicketDTO.from_station=CDW&leftTicketDTO.to_station=ESN&purpose_codes=ADULT'
        global configs
        global fromStation
        global toStation
        print "from %s to %s" % (fromStation, toStation)
        args = {
                'leftTicketDTO.train_date':configs['depart_date'],
                'leftTicketDTO.from_station':fromStation,
                'leftTicketDTO.to_station':toStation,
                'purpose_codes': 'ADULT'
               }
        #leftTicketUrl = '?leftTicketDTO.train_date=2018-01-16&leftTicketDTO.from_station=CDW&leftTicketDTO.to_station=ESN&purpose_codes=ADULT'
        arglist = ['leftTicketDTO.train_date=' + configs['depart_date'],
                   'leftTicketDTO.from_station=' + fromStation,
                   'leftTicketDTO.to_station=' + toStation,
                   'purpose_codes=ADULT'
                    ]
        leftTicketUrl = getLeftTicketsUrl + "?" + '&'.join(arglist)

        result = self.session.get(url=leftTicketUrl, headers=self.headers)
        #print "Tickets query result: %s" % result.content
        content = loads(result.content)
        print "status code: %s" % content['httpstatus']
        candidateTrains = []
        if content['httpstatus'] == 200:
            candidateTrains = content['data']['result']
            if None != configs['train_no'] and '' != configs['train_no']:
                return filter(self.trainFilterByNo, candidateTrains)
            else:
                return candidateTrains

        return []

    def trainFilterByNo(self, train):
        global configs
        fields = train.split('|')
        trainNo = fields[3]
        return trainNo == configs['train_no']

    def handleLeftTickets(self, tickets):
        # '''"cO1H6YX8YGo7g1x%2BwEh2svRjS4MPkj1D7zexIoQEpmpOBn2FhqiWNh9geqO9CqQlhjPUUCCsJRFW%0AtWfgD7tDyEOOK1ujyqffD9TmIqlmOjThaNQ%2BRqFWiUf8XXBR39y5RxueqBDazxq%2B4jTCpZ7jYuEN%0ARQ3iW4jskblQx%2B7EpNQVpzAaVa5Mc9NIB1zz6ka4mVor8uFqrkE72AUYykyKqLL5qbtIp5gQI3yi%0AkQBHFhcYD7F4iRx493WnrFxX2azZ
        #|预订|76000D22440C|
        #D2244|ICW   |FZS  |ICW   |ESN  |06:43 |11:42 |04:59 |Y     |OajMKAzDQz7wEFpkCGrY6GWmEeyx5zQsanidEVx0ZetfcelR
        #3    4始发   5终点  6出发  7到达  8发时   9到时  10历时  11当日  12

        #|20180116 |3 |W1 |01 |07 |0 |0 |  |  |  |  |  |  |有 |   |  |    |无  |20  |   |    |O0M0O0 |OMO  |0",'''
        #13        14 15  16  17  18 19 20 21 22 23 24 25 26  27  28 29   30   31  32   33   34      35
        print u"%3s | %5s | %10s | %10s | %10s | %10s | %10s | %10s" % \
              (u"序号", u"车次", u"出发 - 到达", u"发时 - 到时", u"历时", u"特等座", u"一等座", u"二等座")
        idx = 0
        # POST https://kyfw.12306.cn/otn/login/checkUser
        # POST https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest
        # POST https://kyfw.12306.cn/otn/confirmPassenger/initDc
        # POST https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs
        self.checkUser()
        for ticket in tickets:
            fields = ticket.split('|')
            seceret = fields[0]
            trainNo = fields[2]
            leftTicket	= fields[12]
            idx = idx + 1
            print u"%3s | %5s | %10s | %10s | %10s | %10s | %10s | %10s" % \
                  (idx, fields[3], \
                   STATIONS[fields[6]]['name'] + '-' + STATIONS[fields[7]]['name'], \
                   fields[8] + ' - ' + fields[9], fields[10], \
                   fields[31], fields[31], fields[30])
            self.submitOrder(seceret, STATIONS[fields[6]]['name'], STATIONS[fields[7]]['name'])
            repeatSubmitToken = self.initDc()
            self.getPassengers(repeatSubmitToken)
            withSeatCount, noSeatCount = self.getQueueCount(trainNo, fields[3], fields[15], fromStation, toStation, leftTicket, repeatSubmitToken)
            print "余票：　有座－%s张, 无座－%s张" % (withSeatCount, noSeatCount)

    def checkUser(self):
        # Content-Type	application/x-www-form-urlen
        # DNT: 1
        # Host: kyfw.12306.cn
        # If-Modified-Since	0
        # Referer: https://kyfw.12306.cn/otn/leftTicket/init
        headers = self.headers
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers['DNT'] = '1'
        headers['Host'] = 'kyfw.12306.cn'

        # json:
        # _json_att
        # resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"flag":true},"messages":[],"validateMessages":{}}
        result = self.session.post(url=checkUserUrl, data={'_json_att':''}, headers=headers, verify=False)

    def submitOrder(self, secretStr, fromName, toName):
        headers = self.headers
        headers['Accept'] = "*/*"
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        headers['DNT'] = '1'
        headers['Host'] = 'kyfw.12306.cn'
        #headers['Referer: https://kyfw.12306.cn/otn/leftTicket/init
        #
        data = {
            'secretStr': secretStr,
            'train_date': '2018-02-08',
            'back_train_date': '2018-01-10',
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': fromName,
            'query_to_station_name': toName,
            'undefined': ''
        }
        result = self.session.post(url=submitOrderUrl, data=data, headers=headers, verify=False)

    def initDc(self):
        headers = self.headers
        headers['Accept'] = """text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"""
        headers['Content-Type'] = """application/x-www-form-urlencoded"""
        headers['Upgrade-Insecure-Requests'] = "1"
        headers['DNT'] = '1'
        headers['Host'] = 'kyfw.12306.cn'
        # Referer: https://kyfw.12306.cn/otn/leftTicket/init
        #
        # json _json_att
        result = self.session.post(url=initDcUrl, data={'_json_att':''}, headers=headers, verify=False)
        # var globalRepeatSubmitToken = '7100381b00696bc94607092cbeb28167';
        repeatSubmitToken = re.search("var globalRepeatSubmitToken = '(.*?)';", result.content)
        print "repeat submit token: %s" % repeatSubmitToken
        return repeatSubmitToken

    def getPassengers(self, repeatSubmitToken):
        #  89 #{"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"isExist":true,"exMsg":"","two_isOpenClick":["93","95","97","99"],"other_isOpenClick":["91","93","98","99","95","97"],"normal_passengers":[{"code":"13","passenger_name":"","sex_code":"M","sex_name":"男","born_date":"1900-00-00 00:00:00","country_code":"CN","passenger_id_type_code":"1","passenger_id_type_name":"二代身份证","passenger_id_no":"xxxxxxxx","passenger_type":"1","passenger_flag":"0","passenger_type_name":"成人","mobile_no":"13888888882","phone_no":"","email":"","address":"","postalcode":"","first_letter":"","recordCount":"13","total_times":"99","index_id":"0"},
        headers = self.headers
        headers['Accept'] = "*/*"
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers['DNT'] = '1'
        headers['Host'] = 'kyfw.12306.cn'
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        result = self.session.post(url=getPassengersUrl, data=data, headers=headers, verify=False)

    def checkOrderInfo(self, passengerName, IDNum, phoneNum, repeatSubmitToken):
        # Referer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
        #
        # resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"ifShowPassCode":"N","canChooseBeds":"N","canChooseSeats":"Y","choose_Seats":"OM","isCanChooseMid":"N","ifShowPassCodeTime":"1","submitStatus":true,"smokeStr":""},"messages":[],"validateMessages":{}}
        headers = self.headers
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers['DNT'] = '1'
        headers['Host'] = 'kyfw.12306.cn'
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': 'O,0,1,name,1,xxx,xxx,N',
            'oldPassengerStr': 'name,1,xxxx,1_',
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        result = self.session.post(url=checkOrderInfoUrl, data=data, headers=headers, verify=False)
        print "check order info result: %s" % result.content

    def getQueueCount(self, trainNo, trainCode, trainLocation, fromStation, toStation, leftTicketStr, repeatSubmitToken):
        headers = self.headers
        headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers['DNT'] = '1'
        headers['Host'] = 'kyfw.12306.cn'
        data = {
            'train_date': 'Thu+Feb+08+2018+00:00:00+GMT+0800+(CST)',
            'train_no': trainNo,
            'stationTrainCode': trainCode,
            'seatType': 'O',
            'fromStationTelecode': fromStation,
            'toStationTelecode': toStation,
            'leftTicket': leftTicketStr,
            'purpose_codes': '00',
            'train_location': trainLocation,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': repeatSubmitToken
        }
        result = self.session.post(url=getQueueCountUrl, data=data, headers=headers, verify=False)
        print "get queue count result: %s" % result.content
        # resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,
        # "data":{"count":"0","ticket":"27,144","op_2":"false","countT":"0","op_1":"false"},"messages":[],"validateMessages":{}}
        ticketsCount = (0,0)
        try:
            dict = loads(result.content)
            data = dict['data']
            tickets = data['ticket'].split(',')
            ticketsCount = (tickets[0], tickets[1])
        except BaseException, e:
            print "get queue count failed, error: %s" % e
        return ticketsCount


def parseConfigs():
    global configs
    global username
    global password
    global fromStation
    global toStation
    configFile = './tickets.config'
    with open(configFile, 'r') as f:
        configs = load(f)
        #configs = loads(f.read().decode("utf-8"))
        print u"configs: %s" % configs
    try:
        fromStation = STATIONS[configs['from_station']]['code']
        toStation   = STATIONS[configs['to_station']]['code']
    except BaseException, e:
        print "车站名错误: %s" % e
        sys.exit(-1)
    credFile = './credential.config'
    with open(credFile, 'r') as f:
        creds = load(f)
        username = creds['user_name']
        password = creds['password']

def loopCheckCaptcha():
    chek = False
    #只有验证成功后才能执行登录操作
    while not chek:
        chek = login.checkCaptcha()
        if chek:
            print '验证通过!'
        else:
            print '验证失败，请重新验证!'

def loopLogin():
    loginResult = False
    try:
        loginResult = login.loginTo()
    except:
        pass
    print "login result: %s" % loginResult
    while True != loginResult:
        if "5" == loginResult:
            loopCheckCaptcha()
        else:
            print '登录失败，try again 2 seconds later!'

        time.sleep(2)
        loginResult = False
        try:
            loginResult = login.loginTo()
        except:
            pass
        print "login result: %s" % loginResult

if __name__ == '__main__':
    parseConfigs()
    login = LoginTic()
    login.getImg()
    loopCheckCaptcha()

    loopLogin()
    print '恭喜你，登录成功，可以购票!'
    leftTickets = login.queryLeftTickets()
    while len(leftTickets) < 1:
        print '查询余票失败，try again 2 seconds later!'
        time.sleep(2)
        leftTickets = login.queryLeftTickets()

    login.handleLeftTickets(leftTickets)
