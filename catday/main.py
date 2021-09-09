from machine import Pin
import utime,time
from micropython import const
import network
from microWebSrv import MicroWebSrv
import json
import _thread

import gc
gc.collect()

ap = network.WLAN(network.AP_IF)
ap.ifconfig(('1.2.3.4', '255.255.255.0', '1.2.3.4', '8.8.8.8'))
ap.config(essid="CATDAY",channel=6,authmode=3,password='12345678')
ap.active(True)

_DC_CHAY=const(0)
_DC_DUNG=const(1)
_STEP_EN=const(0)
_STEP_DIS=const(1)
_DIR_T=const(1)
_DIR_N=const(0)
_CT_DA=const(0)
_CT_NHA=const(1)

_STEP_MM_DE=200/155
_T_THEM=const(2000)
_T_CHO=const(10000)

_T_DUTY=const(1000)
_CHIEUDAI=const(700)
_SOLUONG=const(1000)




step=Pin(23,Pin.OUT)
dir=Pin(22,Pin.OUT)
en=Pin(21,Pin.OUT)
dc_cat=Pin(19,Pin.OUT)
ctht=Pin(18,Pin.IN,Pin.PULL_UP)

en.value(_STEP_EN)
dir.value(_DIR_T)
dc_cat.value(_DC_DUNG)



step_mm=_STEP_MM_DE
t_duty=_T_DUTY
duoccat=False#dieu khien dung cat
trangthai="san sang"#bao trang thai cat
speed=180#vong/phut
soluong=_SOLUONG
dacat=0
chieudai=_CHIEUDAI


#DIEU KHIEN DC CAT
def dk_cat(dk):  
  if dk=="on":
    dc_cat.value(_DC_CHAY)
  else:
    dc_cat.value(_DC_DUNG)
#cho động cơ quay, chờ sự kiên hoặc t_cho, cho chạy thêm t_them roi dung dong cơ
def catday(sukien="up",t_them=_T_THEM,t_cho=_T_CHO): 
  sk_value=_CT_DA
  if sukien == "up":
    sk_value=_CT_NHA
  old_value=ctht.value()
  
  _starttime=utime.ticks_ms()
  dk_cat("on")
  while True:
    #kiểm tra thoi gian chơ
    _diff_time=utime.ticks_diff(utime.ticks_ms(),_starttime)
    if _diff_time > t_cho:
      dk_cat("off")
      return "timeout"
    #kiem tra su kien
    _ctht_value = ctht.value()
    if _ctht_value==sk_value and _ctht_value != old_value:
      utime.sleep_ms(100)
      _ctht_value = ctht.value()
      if _ctht_value==sk_value and _ctht_value != old_value:
        #print("cham ctht")
        break
      
      
    old_value = _ctht_value 
    utime.sleep_ms(10)
  #cho them t_them roi dung cat
  utime.sleep_ms(t_them)
  dk_cat("off")
  return "ok"
  
#CAP 1 DAY VOI CHIEU DAI
def capday(chieudai):
  #chon chieu
  if chieudai < 0:
    dir.value(_DIR_N)
  else:
    dir.value(_DIR_T)
  #doi ra buoc
  _sobuoc=abs(chieudai)*step_mm
  #dieu kien cap day
  for i in range(_sobuoc):  
    step.value(1)
    utime.sleep_us(t_duty)
    step.value(0)
    utime.sleep_us(t_duty)

#cat 1 day
def catmotdayday(chieudai):
  capday(chieudai)
  a=catday()
  return a
#cat n day
def catnday(soluong,chieudai):
  global duoccat
  global trangthai
  global dacat
  duoccat=True
  trangthai="dang cat"
  dacat=0
  en.value(_STEP_EN)
  for i in range(soluong):
    if duoccat == False:
      trangthai="san sang"
      en.value(_STEP_DIS)
      break
    a=catmotdayday(chieudai)
    if a != "ok":
      trangthai = a
      duoccat = False
      en.value(_STEP_DIS)
      break
    dacat=dacat+1
  duoccat = False  
  trangthai="san sang"
  en.value(_STEP_DIS)
  
def catnday_thread(soluong,chieudai): 
  global duoccat
  global trangthai
  duoccat=False
  #cho dung cat
  _starttime=utime.ticks_ms()
  #print("trang thai",trangthai)
  while True:
    #kiểm tra thoi gian chơ
    _diff_time=utime.ticks_diff(utime.ticks_ms(),_starttime)
    if _diff_time > _T_CHO:
      trangthai="san sang"
      break
    if trangthai=="san sang":
      break
  #print("so luong cat",soluong)    
  _thread.start_new_thread(catnday, (soluong,chieudai))
  #catnday(soluong,chieudai)
  

#doi vong/phut -> thoi gian xung
def vong_phut_txung(vongphut):
  '''
  duong kinh 50mm->chu vi 155
  toc do 180vong/phut->180*200xung/1*60*1000*1000us=6/10000xung/us
  thoi gian muc cao 10000/12 us
  '''
  txung = int(150000/vongphut)
  return txung
#  
def read_config():
  global step_mm
  global speed
  global chieudai
  try:
    with open('config.json') as f:
      _config=""
      _config=json.load(f)
      f.close()
      #print("config",_config)
      step_mm=_config["step_mm"]
      speed = _config["speed"]
      #print("step_mm1",step_mm)
      t_duty = vong_phut_txung(speed)
      chieudai=_config["chieudai"]

  except:
    #print('error')
    pass
#
def write_config():
  global step_mm
  global speed
  global chieudai
  _strfile=""
  _strfile='{"step_mm":'+str(step_mm)+',"speed":'+str(speed)+',"chieudai":'+str(chieudai)+'}'
  with open('config.json', 'w') as f: 
    f.write(_strfile)
    f.close()
    
 

@MicroWebSrv.route('/')
def handlerimplemented(httpClient, httpResponse) :
  httpResponse.WriteResponseFile('www/index.html', contentType="text/html", headers=None)
  print("trang chu")  
  
@MicroWebSrv.route('/caidat')  
def handlerimplemented(httpClient, httpResponse) :
  httpResponse.WriteResponseFile('www/caidat.html', contentType="text/html", headers=None)
  print("cai dat")  
  
@MicroWebSrv.route('/lenh','POST')  
def handlerimplemented(httpClient, httpResponse) :
  content = httpClient.ReadRequestContent()
  data = json.loads(content)
  mydata={"cmd":"traloi","para":[]}
  global soluong
  global chieudai
  global trangthai
  global duoccat
  global step_mm
  global speed
  global t_duty
  global dacat
  if data["cmd"]=="hoi":
    #print("hoi")
    for i in range(len(data["para"])):
      a=eval(data["para"][i])
      #print(a)
      mydata["para"].append(a)
  elif data["cmd"]=="cat": 

    #print("cat")
    #lay chieu dai+soluong
    soluong=data["para"][0]
    chieudai=data["para"][1]
    #cai + luu chieu dai
    write_config()
    #goi chuong trinh cat n day
    catnday_thread(soluong,chieudai)
    #duoccat=True
    mydata["para"].append("dang cat")
    
  elif data["cmd"]=="dung": 
    #print("dung")

    duoccat=False
    mydata["para"].append("dung cat")
    
  elif data["cmd"]=="caidat":
    #print("cai dat")
    step_mm=data["para"][0]
    speed=data["para"][1]
    t_duty = vong_phut_txung(speed)
    #print("t_duty",t_duty)
    #cai + luu chieu dai
    write_config()
    mydata["para"].append("Da luu thong so")

  httpResponse.WriteResponseJSONOk(obj=mydata, headers=None)
  #print("data ",mydata)   
 
#
@MicroWebSrv.route('/hoilenh')
def handlerimplemented(httpClient, httpResponse) :
  global dacat
  global soluong
  global trangthai
  data= '{"tiendo":"'+str(dacat)+"/"+str(soluong)+'","trangthai":"'+str(trangthai)+'"}'
  #print("data",data)
  httpResponse.WriteResponseOk(
    headers = ({'Cache-Control': 'no-cache'}),
    contentType = 'text/event-stream',
    contentCharset = 'UTF-8',
    content = 'data: {0}\n\n'.format(data) )
  
@MicroWebSrv.route('/cat','POST')  
def handlerimplemented(httpClient, httpResponse) :
  content = httpClient.ReadRequestContent()
  data = json.loads(content)
  mydata={"cmd":"traloi","para":[]}
  global soluong
  global chieudai

  if data["cmd"]=="cat": 

    #print("cat")
    #lay chieu dai+soluong
    soluong=data["para"][0]
    chieudai=data["para"][1]
    #cai + luu chieu dai
    write_config()
    #goi chuong trinh cat n day
    
    mydata["para"].append("dang cat")  
    httpResponse.WriteResponseJSONOk(obj=mydata, headers=None)
    #catnday(soluong,chieudai)
    _thread.start_new_thread(catnday, (soluong,chieudai))
    
  
#
read_config()
#catnday(1,chieudai)
catday()
en.value(_STEP_DIS)

srv = MicroWebSrv(webPath='/www/')
srv.Start(threaded=True)

'''
while True:
  if duoccat==True and trangthai=="san sang":
    catnday(soluong,chieudai)
  utime.sleep(1)
'''

'''
1. kiem tra so moi gui
2. dong co chay bi dap - nghi de trong thread rieng



'''









