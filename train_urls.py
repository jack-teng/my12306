#!/usr/bin/python
# -*- coding: utf-8 -*-

# login init
loginInitUrl = "https://kyfw.12306.cn/otn/login/init"
stationInfoUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'

loginUrl1 = "https://kyfw.12306.cn/passport/web/login"
loginUrl2 = "https://kyfw.12306.cn/otn/login/userLogin"
#getUserLoginUrl = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
getUserLoginUrl = "https://kyfw.12306.cn/otn/login/userLogin"


uamtkUrl = "https://kyfw.12306.cn/passport/web/auth/uamtk"
uamauthclientUrl = "https://kyfw.12306.cn/otn/uamauthclient"

# GET
# headers:
# Cache-Control: no-cache
# DNT: 1
# Host: kyfw.12306.cn
# If-Modified-Since	0
# Referer: https://kyfw.12306.cn/otn/leftTicket/init
# Resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"data":[{"start_station_name":"成都东","arrive_time":"----","station_train_code":"D2244","station_name":"成都东","train_class_name":"动车","service_type":"2","start_time":"06:43","stopover_time":"----","end_station_name":"福州","station_no":"01","isEnabled":true},{"arrive_time":"07:40","station_name":"遂宁","start_time":"07:42","stopover_time":"2分钟","station_no":"02","isEnabled":true},{"arrive_time":"08:32","station_name":"合川","start_time":"08:35","stopover_time":"3分钟","station_no":"03","isEnabled":true},{"arrive_time":"09:00","station_name":"重庆北","start_time":"09:21","stopover_time":"21分钟","station_no":"04","isEnabled":true},{"arrive_time":"09:50","station_name":"长寿北","start_time":"09:52","stopover_time":"2分钟","station_no":"05","isEnabled":true},{"arrive_time":"11:08","station_name":"利川","start_time":"11:10","stopover_time":"2分钟","station_no":"06","isEnabled":true},{"arrive_time":"11:42","station_name":"恩施","start_time":"11:46","stopover_time":"4分钟","station_no":"07","isEnabled":true},{"arrive_time":"12:09","station_name":"建始","start_time":"12:11","stopover_time":"2分钟","station_no":"08","isEnabled":false},{"arrive_time":"13:36","station_name":"宜昌东","start_time":"13:45","stopover_time":"9分钟","station_no":"09","isEnabled":false},{"arrive_time":"14:04","station_name":"枝江北","start_time":"14:06","stopover_time":"2分钟","station_no":"10","isEnabled":false},{"arrive_time":"14:25","station_name":"荆州","start_time":"14:27","stopover_time":"2分钟","station_no":"11","isEnabled":false},{"arrive_time":"15:23","station_name":"汉川","start_time":"15:29","stopover_time":"6分钟","station_no":"12","isEnabled":false},{"arrive_time":"15:56","station_name":"汉口","start_time":"16:07","stopover_time":"11分钟","station_no":"13","isEnabled":false},{"arrive_time":"16:33","station_name":"武汉","start_time":"16:41","stopover_time":"8分钟","station_no":"14","isEnabled":false},{"arrive_time":"17:04","station_name":"鄂州","start_time":"17:06","stopover_time":"2分钟","station_no":"15","isEnabled":false},{"arrive_time":"17:18","station_name":"黄石北","start_time":"17:21","stopover_time":"3分钟","station_no":"16","isEnabled":false},{"arrive_time":"17:29","station_name":"大冶北","start_time":"17:32","stopover_time":"3分钟","station_no":"17","isEnabled":false},{"arrive_time":"17:46","station_name":"阳新","start_time":"17:48","stopover_time":"2分钟","station_no":"18","isEnabled":false},{"arrive_time":"18:27","station_name":"德安","start_time":"18:29","stopover_time":"2分钟","station_no":"19","isEnabled":false},{"arrive_time":"18:59","station_name":"南昌西","start_time":"19:05","stopover_time":"6分钟","station_no":"20","isEnabled":false},{"arrive_time":"19:42","station_name":"抚州","start_time":"19:44","stopover_time":"2分钟","station_no":"21","isEnabled":false},{"arrive_time":"20:28","station_name":"建宁县北","start_time":"20:30","stopover_time":"2分钟","station_no":"22","isEnabled":false},{"arrive_time":"20:43","station_name":"泰宁","start_time":"20:45","stopover_time":"2分钟","station_no":"23","isEnabled":false},{"arrive_time":"21:18","station_name":"三明北","start_time":"21:22","stopover_time":"4分钟","station_no":"24","isEnabled":false},{"arrive_time":"21:40","station_name":"尤溪","start_time":"21:43","stopover_time":"3分钟","station_no":"25","isEnabled":false},{"arrive_time":"22:17","station_name":"永泰","start_time":"22:20","stopover_time":"3分钟","station_no":"26","isEnabled":false},{"arrive_time":"22:45","station_name":"福州","start_time":"22:45","stopover_time":"----","station_no":"27","isEnabled":false}]},"messages":[],"validateMessages":{}}
getTrainDetailUrl = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=76000D22440C&from_station_telecode=ICW&to_station_telecode=ESN&depart_date=2018-02-08'
#
# header
# Referer https://kyfw.12306.cn/otn/czxx/init
# json body:
# module	other
# rand	sjrand
# 0.010997906369456634
# resp: jpeg
getVerifyCodeUrl = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=other&rand=sjrand&0.010997906369456634'
lll = 'https://kyfw.12306.cn/otn/czxx/query?train_start_date=2018-02-09&train_station_name=恩施&train_station_code=ESN&randCode=nNq6'

# get
# headers:
# Cache-Control: no-cache
# DNT: 1
# Host: kyfw.12306.cn
# If-Modified-Since: 0
# Referer: https://kyfw.12306.cn/otn/leftTicket/init
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"messages":[],"validateMessages":{}}
getLeftTicketsLogUrl = 'https://kyfw.12306.cn/otn/leftTicket/log?leftTicketDTO.train_date=2018-02-08&leftTicketDTO.from_station=CDW&leftTicketDTO.to_station=ESN&purpose_codes=ADULT'

# resp
# iEapPfJlO7vlSVa1BUwB7t4tikktwrzmQyVhYT5EOktwLo1iOacujnTYZ03bDydBS%2Bs6v0SzSA7X%0AfCs8%2FRlbJeJaLHDd6bBYZAmDuwSUA0J6BTRHuG8ESK551p69MLQSqC9thdUdDHpsK%2FMsDtNydIzO%0ApLwoWJb16ZNwfRiCix8Bomce0J7bfyH6vJjrpE5gl8KgKuuK50d2nK9BoJJ4WtmNL60YL6iXP%2BbC%0AWqPEVSxAltuu37da3W1pOmLevcJ0fb0IUYw80go%3D|预订|76000D22440C|D2244|ICW|FZS|ICW|ESN|06:43|11:42|04:59|Y|ByyR5GeiUJIZgGro5zy%2BL2ayYMYQiHVq7Nnep10Qkz5wTxuUjhAoprybxjo%3D|20180208|3|W1|01|07|0|0|||||||有||||有|有|无||O090O0M0|O9OM|0
#getLeftTicketsUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=2018-02-08&leftTicketDTO.from_station=CDW&leftTicketDTO.to_station=ESN&purpose_codes=ADULT'
getLeftTicketsUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'

# POST
# headers:
# Content-Type	application/x-www-form-urlen
# DNT: 1
# Host: kyfw.12306.cn
# If-Modified-Since	0
# Referer: https://kyfw.12306.cn/otn/leftTicket/init

# json:
# _json_att
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"flag":true},"messages":[],"validateMessages":{}}
checkUserUrl = 'https://kyfw.12306.cn/otn/login/checkUser'

# post
# header:
# Accept: */*
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# DNT: 1
# Host: kyfw.12306.cn
# Referer: https://kyfw.12306.cn/otn/leftTicket/init
#
# json:
# secretStr	BEo/wVPAwb1D0Gsyhkup7UzjC+gFoWlMsvTcKLYXRZ/cFqbEyuyE1CF67NTlJ+hKwcP0hueIVHCf Yg//Q4NgwE4d9IzDlkl7mm3t4hStjoXNnAjeiLBOwJ1z3470oEdSbumtiyiPkRhDgRDh+gSl7nMD 8/qlqPr7781mcjRz8adjVm5BEgNVrd0drIFcBXo+4ZMBC7hztkLJQbYaWF3IGVwCEo4eZGjChZon TOmtaj+9AmWIaWOctaQuBkJ2cTRxllDgpCUMVEA=
# train_date	2018-02-08
# back_train_date	2018-01-10
# tour_flag	dc
# purpose_codes	ADULT
# query_from_station_name	成都
# query_to_station_name	恩施
# undefined
#
# resp: {"validateMessagesShowId":"_validatorMessage","status":false,"httpstatus":200,"messages":["车票信息已过期，请重新查询最新车票信息"],"validateMessages":{}}
# resp ok: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":"N","messages":[],"validateMessages":{}}
submitOrderUrl = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'

# post
# headers
# Accept: text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8
# Content-Type	application/x-www-form-urlencoded
# DNT: 1
# Host: kyfw.12306.cn
# Referer: https://kyfw.12306.cn/otn/leftTicket/init
# Upgrade-Insecure-Requests	1
#
# json _json_att
initDcUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
#
# post
# headers:
# Accept: */*
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# DNT: 1
# Host: kyfw.12306.cn
# Referer: https://kyfw.12306.cn/otn/leftTicket/init
#
# json:
# _json_att	
# REPEAT_SUBMIT_TOKEN	a26b59b893084f00fff0cfb47aa02c8f
#
# resp:
#  89 #{"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"isExist":true,"exMsg":"","two_isOpenClick":["93","95","97","99"],"other_isOpenClick":["91","93","98","99","95","97"],"normal_passengers":[{"code":"13","passenger_name":"","sex_code":"M","sex_name":"男","born_date":"1900-00-00 00:00:00","country_code":"CN","passenger_id_type_code":"1","passenger_id_type_name":"二代身份证","passenger_id_no":"xxxxxxxx","passenger_type":"1","passenger_flag":"0","passenger_type_name":"成人","mobile_no":"13888888882","phone_no":"","email":"","address":"","postalcode":"","first_letter":"","recordCount":"13","total_times":"99","index_id":"0"},

getPassengersUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'

# post
# Header:
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# DNT: 1
# Host: kyfw.12306.cn
# Referer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
#
# params:
# cancel_flag: 2
# cancel_flag	2
# bed_level_order_num	000000000000000000000000000000
# passengerTicketStr	O,0,1,张三,1,id_num,13888888888,N
# oldPassengerStr	张三,1,id_num,1_
# tour_flag	dc
# randCode
# whatsSelect	1
# _json_att
# REPEAT_SUBMIT_TOKEN	d362cf95cd789ad8773d841a62b28527
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"ifShowPassCode":"N","canChooseBeds":"N","canChooseSeats":"Y","choose_Seats":"OM","isCanChooseMid":"N","ifShowPassCodeTime":"1","submitStatus":true,"smokeStr":""},"messages":[],"validateMessages":{}}
checkOrderInfoUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'

# post
# Header:
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# DNT: 1
# Host: kyfw.12306.cn
# refer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
#
# train_date	Thu+Feb+08+2018+00:00:00+GMT+0800+(CST)
# train_no	76000D22440C
# stationTrainCode	D2244
# seatType	O
# fromStationTelecode	ICW
# toStationTelecode	ESN
# leftTicket	V0R%2FvTGjZVN%2Fc8j4OnKKl5KdjqxUuT1QHZBrA3qhLeJW162f1Ty1T34cxAg%3D
# leftTicket	QCc5ff%2F56tgbxBJT1zj43F%2FMV0WliUxgOfU8nExBUio5X%2FPoqa0%2FCU%2FN8z8%3D
# purpose_codes	00
# train_location	W1
# _json_att
# REPEAT_SUBMIT_TOKEN	d362cf95cd789ad8773d841a62b28527
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"count":"0","ticket":"27,144","op_2":"false","countT":"0","op_1":"false"},"messages":[],"validateMessages":{}}
getQueueCountUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'

# post
# Header:
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# DNT: 1
# Host: kyfw.12306.cn
# refer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
#
# json body:
# passengerTicketStr	O,0,1,张三,1,id_num,13888888888,N
# oldPassengerStr	张三,1,id_num,1_
# randCode
# purpose_codes	00
# key_check_isChange	63AA3C222C7B0A03A82F0B017CC30653FD38514FB840A5DFAB8893FA
# leftTicketStr	V0R%2FvTGjZVN%2Fc8j4OnKKl5KdjqxUuT1QHZBrA3qhLeJW162f1Ty1T34cxAg%3D
# train_location	W1
# choose_seats	1F
# seatDetailType	000
# whatsSelect	1
# roomType	00
# dwAll	N
# _json_att
# REPEAT_SUBMIT_TOKEN	d362cf95cd789ad8773d841a62b28527
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"submitStatus":true},"messages":[],"validateMessages":{}}
confirmOrderUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'

# get
# https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=1515558536682&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=d362cf95cd789ad8773d841a62b28527
# Header:
# refer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"queryOrderWaitTimeStatus":true,"count":0,"waitTime":4,"requestId":6356713219127279176,"waitCount":0,"tourFlag":"dc","orderId":null},"messages":[],"validateMessages":{}}
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"queryOrderWaitTimeStatus":true,"count":0,"waitTime":-1,"requestId":6356713219127279176,"waitCount":0,"tourFlag":"dc","orderId":"E789171113"},"messages":[],"validateMessages":{}}
#queryOrderUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=1515558533634&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=d362cf95cd789ad8773d841a62b28527'
queryOrderStateWaitTimeUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'

# post
# refer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
# orderSequence_no	E789171113
# _json_att
# REPEAT_SUBMIT_TOKEN	d362cf95cd789ad8773d841a62b28527
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"submitStatus":true},"messages":[],"validateMessages":{}}
resultOrderForDcQueueUrl = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'

# post
# Header:
# refer: https://kyfw.12306.cn/otn/confirmPassenger/initDc
# Upgrade-Insecure-Requests	1
# JSON: 
# _json_att
# REPEAT_SUBMIT_TOKEN	d362cf95cd789ad8773d841a62b28527
# resp: 等待付款界面
payOrderInitUrl = 'https://kyfw.12306.cn/otn//payOrder/init?random=1515558537928'

# method: post

# headers:
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# DNT: 1
# Host: kyfw.12306.cn
# Referer: https://kyfw.12306.cn/otn//payOrder/init?random=1515562040967
#
# json body:
# sequence_no	E111111111
# parOrderDTOJson	{"sequence_no":"E111111111","order_date":"2018-01-10+00:00:00","ticket_totalnum":1,"ticket_price_all":19600.0,"epayFlag":"Y","orders":[{"sequence_no":"E111111111","order_date":"2018-01-10+00:00:00","ticket_totalnum":1,"ticket_price_all":19600.0,"tickets":[{"stationTrainDTO":{"station_train_code":"D2244","from_station_telecode":"ICW","from_station_name":"成都东","start_time":"1970-01-01+06:43:00","to_station_telecode":"ESN","to_station_name":"恩施","arrive_time":"1970-01-01+11:42:00","distance":"652"},"passengerD…6826","amount":"19600","amount_char":1,"start_train_date_page":"2018-02-08+06:43","str_ticket_price_page":"196.0","come_go_traveller_ticket_page":"N","return_rate":"0","return_deliver_flag":"N","deliver_fee_char":"","is_need_alert_flag":false,"is_deliver":"00","dynamicProp":"","return_fact":0.0,"fee_char":"","sepcial_flags":"","column_nine_msg":"","integral_pay_flag":"N"}],"isNeedSendMailAndMsg":"N","ticket_total_price_page":"196.0","come_go_traveller_order_page":"N","canOffLinePay":"N","if_deliver":"N"}]}
# orderRequestDTOJson	{"bureau_code":"W","train_location":"W1","train_date":"2018-02-08+00:00:00","train_no":"76000D22440C","station_train_code":"D2244","from_station_telecode":"ICW","to_station_telecode":"ESN","from_station_name":"成都东","to_station_name":"恩施","seat_type_code":"O","seat_detail_type_code":"0","start_time":"1970-01-01+06:43:00","end_time":"1970-01-01+11:42:00","adult_num":0,"child_num":0,"student_num":0,"disability_num":0,"ticket_num":0,"id_mode":"Y","reserve_flag":"A","tour_flag":"dc","reqIpAddress":"125.70.163.17","reqTimeLeftStr":"00ICWESN成都东恩施76000D22440C2018-02-08D2244","realleftTicket":"O0196000259058800000O019603144M023500112","choose_seat":"1A","isShowPassCode":"N&2&default","passengerFlag":"1","exchange_train_flag":"0","channel":"E"}
# _json_att	
#
# resp: {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"cancelStatus":true},"messages":[],"validateMessages":{}}
cancelOrderUrl = 'https://kyfw.12306.cn/otn/payOrder/cancel'

logoutUrl = "https://kyfw.12306.cn/otn/login/loginOut"
