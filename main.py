# bluething-sensor
#
# This code reads the temperature from an MCP9808 and sends it via MQTT to
# a remote server. Then the device is send into deep sleep to be able to
# run from a battery for a long time.
#
# Developed and tested with an Adafruit Feather HUZZAH and Adafruit MCP9808
# on MicroPython 1.8.6

from machine import Pin, I2C
from mcp9808 import MCP9808, T_RES_AVG
from umqtt.simple import MQTTClient
import time
import utime
import network
import ubinascii
import machine
import ntptime

WLAN_SSID = "<your-ssid>"
WLAN_PSK = "<pre-shared-key>"

MQTT_HOST = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASS = ""

NTP_HOST = "pool.ntp.org"

# Interval to measure temperature (minutes)
SEND_INTERVAL = 1


def connectWiFi():
   sta_if = network.WLAN(network.STA_IF)

   if not sta_if.isconnected():
      print('connecting to network ...')
      sta_if.active(True)
      sta_if.connect(WLAN_SSID, WLAN_PSK)

      while not sta_if.isconnected():
         time.sleep_ms(50)

   print('network config: ', sta_if.ifconfig())

def getDeviceId():
   return "ESP8266-{}".format(ubinascii.hexlify(machine.unique_id()))

def pubMQTT(temperature, timestamp):
   c = MQTTClient(getDeviceId(), MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS)
   c.connect()
   c.publish("/sensors/{}/temperature".format(getDeviceId()), "{}|{}".format(timestamp, temperature), False, 1)
   c.disconnect()

def getTemperature():
   i2c = I2C(Pin(5), Pin(4))

   sensor = MCP9808(i2c)
   sensor.set_shutdown_mode(False)
   sensor.set_resolution(T_RES_AVG)

   # give it some time to measure
   time.sleep_ms(130)

   temp = sensor.get_temp()
   sensor.set_shutdown_mode(True)

   return temp

def sleepToFullMinute(minutes):
   localtime = utime.localtime(utime.time() + minutes*60)
   return minutes*60 - localtime[5] + 30

def deepsleep(sleepsec):
   rtc = machine.RTC()
   rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
   rtc.alarm(rtc.ALARM0, sleepsec*1000)

   # this will actually do a reset
   machine.deepsleep()

def unixTimestamp():
   # Offset Unix timestamp (1.1.1970) to RTC (1.1.2000)
   RTC_OFFSET = 946684800
   return utime.time()+RTC_OFFSET


temp = getTemperature()
print('Temp: ', temp)

connectWiFi()

ntptime.host = NTP_HOST
ntptime.settime()

lt = utime.localtime()
print('{}/{}/{} {}:{}:{}'.format(lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]))

pubMQTT("{:.1f}".format(temp), unixTimestamp())

# this will result in a reset
deepsleep(sleepToFullMinute(SEND_INTERVAL))
