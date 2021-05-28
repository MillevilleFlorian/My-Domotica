# from Code.Backend.help.KlasseLCD import LCD
import time
from typing import ItemsView
from RPi import GPIO
from help.KlasseSpi import SPi
from help.KlasseLCD import LCD
import threading

from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify
from repositories.DataRepository import DataRepository


# Code voor Hardware
vent = 26
lamp = 20
buzzer = 21

teller = 0
buzz = 0
vorige_temp = 0
lamp_stand = 0


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(vent,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.setup(lamp,GPIO.OUT)

GPIO.output(vent,GPIO.LOW)
GPIO.output(buzzer, GPIO.LOW)
GPIO.output(lamp,GPIO.LOW)


spi = SPi()
lcd = LCD()
lcd.init_LCD()

# Code voor Flask 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)

CORS(app) 


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(e)
    spi.closespi()


# START een thread op. Belangrijk!!! Debugging moet UIT staan op start van de server, anders start de thread dubbel op
# werk enkel met de packages gevent en gevent-websocket.
def all_out():
    while True:
        global vorige_temp
        global lamp_stand
        global teller
        global buzz
        
        temp = spi.read_bytes(0)
        beweging = spi.read_bytes(1)
        rook = spi.read_bytes(2)
        temperatuur = round((((temp / 1023 * 3000)-500) /10), 1)
        # -----------------
        if beweging > 10:
            DataRepository.add_meting_beweging(beweging)
        DataRepository.add_meting_rook(rook)
        if temperatuur !=  vorige_temp:
            DataRepository.add_meting_temp(temperatuur)
        vorige_temp = temperatuur
        # -----------------
        socketio.emit('B2F_data_beweging',{'beweging': beweging})
        socketio.emit('B2F_data_temp', {'temp': temperatuur})
        socketio.emit('B2F_data_rook', {'rook': rook})
        # -----------------
        print(f'rook = {rook}')
        print(f'beweging = {beweging}')
        print(f'temperatuur = {temperatuur}')
        print(f'Ventilator = {teller}')
        print(f'Buzzer = {buzz}')
        print(f'Lamp = {lamp_stand}')
        print('------------')
        # -----------------
        lcd.send_message(f'Temp:{temperatuur} Graden')
        # print(waarde)
        time.sleep(1)


thread = threading.Timer(1, all_out)
thread.start()


print("**** Program started ****")

# API ENDPOINTS


@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


@socketio.on('connect')
def initial_connection():
    global vorige_temp
    print('A new client connect')
    # # Send to the client!
    # vraag de status op van de lampen uit de DB
    temp = DataRepository.read_status_temp()
    vorige_temp = temp
    # print(temp['waarde'])
    socketio.emit('B2F_data_temp', {'temp': temp['waarde']})


# FUNCTIES

@socketio.on('F2B_vent_click')
def switch_vent(data):
    global teller
    teller = data['stand']
    if data['stand'] == 1:
        GPIO.output(vent, GPIO.HIGH)
        DataRepository.add_stand_vent(1)
    else:
        GPIO.output(vent,GPIO.LOW)
        DataRepository.add_stand_vent(0)

@socketio.on('F2B_buzzer_click')
def switch_buzzer(data):
    global buzz
    buzz = data['stand']
    if data['stand'] == 1:
        GPIO.output(buzzer, GPIO.HIGH)
        DataRepository.add_stand_buzzer(1)
    else:
        GPIO.output(buzzer,GPIO.LOW)
        DataRepository.add_stand_buzzer(0)

@socketio.on('F2B_lamp_click')
def switch_buzzer(data):
    global lamp_stand
    lamp_stand = data['stand']
    if data['stand'] == 1:
        GPIO.output(lamp, GPIO.HIGH)
        DataRepository.add_stand_lamp(1)
    else:
        GPIO.output(lamp,GPIO.LOW)
        DataRepository.add_stand_lamp(0)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
