#-*- coding: utf-8 -*-
'''
@author: matsuyamanori@gmail.com
'''

import urllib
import time
import json
import threading
from ws4py.client.threadedclient import WebSocketClient
from tplight import KL130

class SmartLight(WebSocketClient):
    def __init__(self, url, lightIP):
        print('*** __init__')
        self.url = url
        self.count = 0
        self.lastMessage = None
        self.light = KL130(lightIP)
        self.light.ransition_period = 0
        self.light.off()
        self.light.brightness = 100
        self.light.saturation = 100
        print(self.light.model)
        super().__init__(url, protocols=['http-only', 'chat'])

    def go(self):
        print('*** go')
        t = threading.Thread(target=self.go_sub)
        t.start()

    def go_sub(self):
        print('*** go_sub')
        self.connect()
     #   self.run_forever
        
    def opened(self):
        print("*** opened")

    def stop(self):
        print('*** stop')
        self.close()
 
    def closed(self, code, reason=None):
        print('*** closed:' + str(code) + ':' + reason)
        if code == 1006 :
            raise TimeoutError(str(code) + ':' + reason)
       
    def received_message(self, message):
        print('*** received_message')
        if len(message.data) > 0:    
            self.count += 1
            self.lastMessage = json.loads(message.data)
            print(self.lastMessage)
            try:
                switch = self.lastMessage[1]['value']['value']['LightSwitchState']
                color = self.lastMessage[1]['value']['value']['LightColor']
                self.lightControl(switch, color)
            except (KeyError, TypeError) as e:
                print('*** received_message:except:' + str(self.lastMessage))
                print(e)

    def unhandled_error(self, error):
        print('*** unhandled_error:', error)
    
    def showLastMessage(self):
        print('*** showLastMessage')
        last = self.lastMessage
        print(str(self.count) + ':' + json.dumps(last, ensure_ascii=False))
    
    def lightControl(self, switch, color):
        print('*** lightSwith')
        if switch == False:
            self.light.off()
        else :
            self.light.on()
            if color == 'White' :
                self.light.temperature = 9000
            elif color == 'Red' :
                for _ in range(10):
                    self.light.hsb = (10, 100, 100)  
                    time.sleep(0.5)
                    self.light.hsb = (0, 0, 0) 
                    time.sleep(0.5)
                self.light.hsb = (10, 100, 100)  
 
                                   
if __name__ == '__main__':
    lightIP = '192.168.1.9'
    url   = 'wss://aitc2.dyndns.org'
    query = '/openmasami/sample01/read/path/1F/居間/照明'
    agent = [ ('AGENTID', 'Receive.py') ]
    endPoint = url + urllib.parse.quote(query.encode('utf-8')) + '?' + urllib.parse.urlencode(agent)
    print(endPoint)
    while True:
        try:
            smartLight = SmartLight(endPoint, lightIP)
            smartLight.go()
            while True:
                input()
                smartLight.showLastMessage()
        except TimeoutError as e:
            print('*** TimeoutError:', e)    
        except KeyboardInterrupt:
            smartLight.lightControl(False, 'XXX')
            smartLight.stop()
            exit(1)


