import time
from RPi import GPIO
from help.KlasseSpi import SPi
import threading

from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify
from repositories.DataRepository import DataRepository


# Code voor Hardware
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

spi = SPi()


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
        temp = spi.read_bytes(0)
        beweging = spi.read_bytes(1)
        rook = spi.read_bytes(2)

        temperatuur = round((((temp / 1023 * 3)-0.5) * 100), 0)
        # -----------------
        DataRepository.add_meting_temp(temperatuur)
        if beweging > 10:
            DataRepository.add_meting_beweging(beweging)
        DataRepository.add_meting_rook(rook)
        # -----------------
        socketio.emit('B2F_data_beweging',{'beweging': beweging})
        socketio.emit('B2F_data_temp', {'temp': temperatuur})
        socketio.emit('B2F_data_rook', {'rook': rook})
        # -----------------
        print(f'rook = {rook}')
        print(f'beweging = {beweging}')
        print(f'temperatuur = {temperatuur}')
        print('------------')
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
    print('A new client connect')
    # # Send to the client!
    # vraag de status op van de lampen uit de DB
    temp = DataRepository.read_status_temp()
    # print(temp['waarde'])
    socketio.emit('B2F_data_temp', {'temp': temp['waarde']})


@socketio.on('F2B_switch_light')
def switch_light(data):
    # Ophalen van de data
    lamp_id = data['lamp_id']
    new_status = data['new_status']
    print(f"Lamp {lamp_id} wordt geswitcht naar {new_status}")

    # Stel de status in op de DB
    res = DataRepository.update_status_lamp(lamp_id, new_status)

    # Vraag de (nieuwe) status op van de lamp en stuur deze naar de frontend.
    data = DataRepository.read_status_lamp_by_id(lamp_id)
    socketio.emit('B2F_verandering_lamp', {'lamp': data}, broadcast=True)

    # Indien het om de lamp van de TV kamer gaat, dan moeten we ook de hardware aansturen.
    if lamp_id == '3':
        print(f"TV kamer moet switchen naar {new_status} !")
        GPIO.output(led3, new_status)

# ANDERE FUNCTIES


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
