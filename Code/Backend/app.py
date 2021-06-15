from os import posix_fallocate
import time
from typing import ItemsView
from RPi import GPIO
from help.KlasseSpi import SPi
from help.KlasseLCD import LCD
import threading
from subprocess import check_output

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
tijd = 0
positie = 0
vent_stand = 0


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(vent, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(lamp, GPIO.OUT)

GPIO.output(vent, GPIO.LOW)
GPIO.output(buzzer, GPIO.LOW)
GPIO.output(lamp, GPIO.LOW)


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
    ip = check_output(['hostname', '--all-ip-addresses'])
    ip = str(ip)
    lcd.send_message(f'{ip[18:31]}')
    while True:
        global vorige_temp
        global lamp_stand
        global teller
        global buzz
        global tijd
        global positie
        global vent_stand

        temp = spi.read_bytes(0)
        beweging = spi.read_bytes(1)
        rook = spi.read_bytes(2)
        temperatuur = round((((temp / 1023 * 3200)-500) / 10), 1)
        # -----------------
        if beweging > 10:
            DataRepository.add_meting_beweging(beweging)
            if lamp_stand == 1:
                pass
            else:
                GPIO.output(lamp, GPIO.HIGH)
                DataRepository.add_stand_lamp(1)
                tijd = 0
                positie = 1
        if rook > 300:
            DataRepository.add_meting_rook(rook)
        if temperatuur != vorige_temp:
            DataRepository.add_meting_temp(temperatuur)
        vorige_temp = temperatuur
        # -----------------
        tab_rook = DataRepository.read_all_rook()
        tab_alarm = DataRepository.read_all_alarm()
        gew_temp = DataRepository.read_gew_temp()
        # -----------------
        socketio.emit('B2F_data_temp', {'temp': temperatuur})
        socketio.emit('B2F_data_tab_rook',  tab_rook)
        socketio.emit('B2F_data_tab_alarm', tab_alarm)
        # -----------------
        print(f'rook = {rook}')
        # print(f'beweging = {beweging}')
        print(f'Ventilator = {teller}')
        print(f'Buzzer = {buzz}')
        print(f'Lamp = {lamp_stand}')
        print('------------')
        # -----------------
        bit_op = 0x80 | 0x40
        lcd.send_instruction(bit_op)
        # ip = check_output(['hostname', '--all-ip-addresses'])
        # ip = str(ip)
        lcd.send_message(f'Temp:{temperatuur} Graden')
        if temperatuur > gew_temp['waarde']:
            GPIO.output(vent, GPIO.HIGH)
            DataRepository.add_stand_vent(1)
            vent_stand = 1
        else:
            if vent_stand == 1:
                GPIO.output(vent, GPIO.LOW)
                DataRepository.add_stand_vent(0)

        # print(waarde)
        if positie == 1:
            tijd += 1
            if tijd == 10:
                tijd = 0
                positie = 0
                GPIO.output(lamp, GPIO.LOW)
                DataRepository.add_stand_lamp(0)
        time.sleep(1)


thread = threading.Timer(15, all_out)
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
    tab_rook = DataRepository.read_all_rook()
    tab_alarm = DataRepository.read_all_alarm()
    gew_temp = DataRepository.read_gew_temp()
    vorige_temp = temp
    # print(temp['waarde'])
    socketio.emit('B2F_data_temp', {'temp': temp['waarde']})
    socketio.emit('B2F_data_tab_rook',  tab_rook)
    socketio.emit('B2F_data_tab_alarm', tab_alarm)
    socketio.emit('B2F_data_gew_temp', gew_temp)
    # -------------------------------

# FUNCTIES

# @socketio.on('F2B_vent_click')
# def switch_vent(data):
#     global teller
#     teller = data['stand']
#     if data['stand'] == 1:
#         GPIO.output(vent, GPIO.HIGH)
#         DataRepository.add_stand_vent(1)
#     else:
#         GPIO.output(vent, GPIO.LOW)
#         DataRepository.add_stand_vent(0)


@socketio.on('F2B_buzzer_click')
def switch_buzzer(data):
    global buzz
    buzz = data['stand']
    if data['stand'] == 1:
        GPIO.output(buzzer, GPIO.HIGH)
        DataRepository.add_stand_buzzer(1)
    else:
        GPIO.output(buzzer, GPIO.LOW)
        DataRepository.add_stand_buzzer(0)


@socketio.on('F2B_lamp_click')
def switch_lamp(data):
    global positie
    global tijd
    global lamp_stand
    lamp_stand = data['stand']
    if data['stand'] == 1:
        GPIO.output(lamp, GPIO.HIGH)
        DataRepository.add_stand_lamp(1)
        positie = 0
        tijd = 0
    else:
        GPIO.output(lamp, GPIO.LOW)
        DataRepository.add_stand_lamp(0)
        positie = 0
        tijd = 0


@socketio.on('F2B_gew_temp')
def gew_temp(data):
    print(data)
    DataRepository.add_gew_temp(data)


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
