#import module
import bluetooth
import time
from ble_advertising import advertising_payload


import network

ssid = 'MicroPython-AP'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)



from micropython import const
# hằng số irq
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(1 << 2)
_IRQ_GATTS_INDICATE_DONE = const(20)

#uuid cho services và char
UART_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
UART_TRX = (bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E'), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY | bluetooth.FLAG_WRITE,)
UART_SERVICE = (UART_UUID, (UART_TRX,),)
SERVICES = (UART_SERVICE,)

#_ADV_APPEARANCE_GENERIC_THERMOMETER = const(999)


class BLEUART:
  def __init__(self, ble, name="mpy-ble"):
    self._ble = ble
    self._ble.active(True)
    self._ble.irq(handler=self._irq)
    ((self._trx,),) = self._ble.gatts_register_services(SERVICES)
    self._connections = set()
    self._payload = advertising_payload(
      name=name, services=[UART_UUID]#, appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER
    )
    self._advertise()
  #các sự kiện Ble tự gọi hàm ngắt
  def _irq(self, event, data):
    # Track connections so we can send notifications.
    if event == _IRQ_CENTRAL_CONNECT:
      conn_handle, _, _ = data
      print("conn_handle",conn_handle)
      self._connections.add(conn_handle)
      print("len _connections",len(self._connections))
      for conn_handle in self._connections:
        print("_connection",conn_handle)
    elif event == _IRQ_CENTRAL_DISCONNECT:
      conn_handle, _, _ = data
      self._connections.remove(conn_handle)
      # Start advertising again to allow a new connection.
      self._advertise()
    elif event == _IRQ_GATTS_INDICATE_DONE:
      conn_handle, value_handle, status = data
    elif event == _IRQ_GATTS_WRITE:
      # The central device has written this feature or descriptor
      conn_handle, attr_handle = data
      print("conn_handle",conn_handle)
      print("attr_handle",attr_handle)
  #
  def write(self, data, notify=False, indicate=False):
    data=b'!' + data
    self._ble.gatts_write(self._trx, data)
    if notify or indicate:
      for conn_handle in self._connections:
        if notify:
          # Notify connected centrals.
          self._ble.gatts_notify(conn_handle, self._trx)
        if indicate:
          # Indicate connected centrals.
          self._ble.gatts_indicate(conn_handle, self._trx)
  def read(self):
    _data = self._ble.gatts_read(self._trx)
    if len(_data)<1:
      return None
    if chr(_data[0])==':':
      return _data
    else:  
      return None
  def _advertise(self, interval_us=500000):
    print("payload: ",self._payload)
    self._ble.gap_advertise(interval_us, adv_data=self._payload)


def demo():
  ble = bluetooth.BLE()
  ble_uart = BLEUART(ble,name="BLEUART")

  while True:
    _ble_data = ble_uart.read()

    if _ble_data is not None:
      print("_ble_data 1 ",_ble_data)
      ble_uart.write(_ble_data,True)
        
    time.sleep_ms(1000)


if __name__ == "__main__":
  demo()









