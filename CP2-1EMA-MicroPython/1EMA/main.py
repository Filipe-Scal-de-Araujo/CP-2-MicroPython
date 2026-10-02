import network, time, json, sys, io
import ubinascii, machine
from machine import Pin, I2C
from i2c_lcd import I2cLcd
from umqtt.simple import MQTTClient

try:
    import requests
except ImportError:
    import urequests as requests

SSID = "Wokwi-GUEST"
PASSWORD = ""
API_KEY = "8e395c62930537ba3fccb9439e255490"
CIDADE = "Sao%20Paulo,BR"
URL = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric"

BROKER = "broker.hivemq.com"
TOPICO = b"fiap/cp2/Filipe_Scal/clima"
CLIENT_ID = b"esp32-" + ubinascii.hexlify(machine.unique_id())

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, 0x27, 4, 20)

def mostrar(l0="", l1="", l2="", l3=""):
    lcd.clear()
    for i, txt in enumerate((l0, l1, l2, l3)):
        lcd.move_to(0, i)
        lcd.putstr(txt[:19])

def mostrar_longo(txt, pausa=4):
    linhas = [txt[i:i+19] for i in range(0, len(txt), 19)]
    for i in range(0, len(linhas), 4):
        mostrar(*linhas[i:i+4])
        time.sleep(pausa)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(1)
    return wlan.isconnected()

def buscar_clima():
    r = requests.get(URL.format(CIDADE, API_KEY))
    try:
        if r.status_code != 200:
            return None, r.status_code
        return r.json(), 200
    finally:
        r.close()

def conectar_mqtt():
    c = MQTTClient(CLIENT_ID, BROKER, port=1883, keepalive=60)
    c.connect()
    return c

mostrar("Conectando WiFi...")
if not conectar_wifi():
    mostrar("Falha no WiFi")
    raise SystemExit

mostrar("Conectando MQTT...")
client = None
try:
    client = conectar_mqtt()
except Exception as e:
    mostrar("Falha no MQTT")
    time.sleep(3)

while True:
    try:
        dados, status = buscar_clima()
        if dados is None:
            mostrar("Erro na API", "Codigo: " + str(status))
        else:
            temp = dados["main"]["temp"]
            umid = dados["main"]["humidity"]
            vento = dados["wind"]["speed"]
            ceu = dados["weather"][0]["main"]

            mostrar(
                dados["name"],
                "Temp: {:.1f} C".format(temp),
                "U:{}% V:{}m/s".format(umid, vento),
                ceu,
            )

            msg = json.dumps({
                "cidade": dados["name"],
                "temp": temp,
                "umidade": umid,
                "vento": vento,
                "ceu": ceu,
            })
            try:
                if client is None:
                    client = conectar_mqtt()
                client.publish(TOPICO, msg)
            except Exception:
                client = None   # tenta reconectar no próximo ciclo
    except Exception as e:
        buf = io.StringIO()
        sys.print_exception(e, buf)
        mostrar_longo(buf.getvalue().replace("\n", " "))
    time.sleep(0.5)