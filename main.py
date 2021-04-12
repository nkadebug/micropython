import time,machine,ntptime,network,ujson

led = machine.Pin(2,machine.Pin.OUT)
relay = machine.Pin(0,machine.Pin.OUT)
led.off()
relay.off()
op = 0

rtc = machine.RTC()

def get_info():
    f = open('info.txt')
    txt = f.read()
    f.close()
    return ujson.loads(txt)

info = get_info()
# print(info)
tsync = False

ap = network.WLAN(network.AP_IF)
ap.config(essid=info['ap']['ssid'], password=info['ap']['pwd'], hidden=info['ap']['hidden'])
ap.active(True)

sta = network.WLAN(network.STA_IF)
sta.active(True)

for a in info['sta']:
    if not sta.isconnected():
        print('Connecting to %s' % a['ssid'])
        sta.connect(a['ssid'], a['pwd'])
        r = 0
        while not sta.isconnected() and r < info['sta_retry']:
            if r:print('.')
            led.off()
            time.sleep(0.1)
            led.on()
            time.sleep(0.2)
            r += 0.2

if sta.isconnected():
    print('Connected: %s [ip: %s]' % (a['ssid'],sta.ifconfig()[0]))
    try:
        ntptime.host = "in.pool.ntp.org"
        ntptime.settime()
        print(time.time())
        print('Time Sync : Successful')
        tsync = True
        sta.active(False)
    except:
        print('Time Sync : Network Error')
    
    if tsync:
        while True:
            info = get_info()
            t = time.localtime()
            h = t[3]+5
            m = t[4]+30
            if m>59:
                h += 1
                m -= 60
            if h>23:
                h -= 24
            hm = '{:2d}:{:2d}'.format(h,m)
            
            try:
                op = 0 if info['seq'][hm] == "on" else 1
                msg = info['seq'][hm]
            except:
                msg = 'No Change'
            
            print('%s:%s - %s - %s' % (hm,t[5],op,msg))
            relay.value(op)
            
            led.off()
            time.sleep(0.1)
            led.on()
            time.sleep(1.9)
else:
    print('Wifi connection failed')




