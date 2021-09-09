import network
from microWebSrv import MicroWebSrv
import json


import gc
gc.collect()

ap = network.WLAN(network.AP_IF)
ap.ifconfig(('1.2.3.4', '255.255.255.0', '1.2.3.4', '8.8.8.8'))
ap.config(essid="CATDAY",channel=6,authmode=3,password='12345678')
ap.active(True)

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
  mydata={"data":"thanh cong"}
  httpResponse.WriteResponseJSONOk(obj=mydata, headers=None)
  print("data ",data)  

srv = MicroWebSrv(webPath='/www/')
srv.Start(threaded=False)


