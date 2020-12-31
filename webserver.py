from marble import Marble
from racecontrol import RacecontrolThread
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit


class MarbleList:

    def __init__(self):
        self.marbles = []

    def append(self, marble):
        self.marbles.append(marble)
        table(True)

    def get(self, i):
        return self.marbles[i]

    def broadcast(self):
        table(True)

    def get_by_id(self, id):
        for marble in self.marbles:
            if marble.id == id:
                return marble
        return None

    def get_marble_with_best_lap(self):
        best_marble = self.marbles[0]
        for marble in self.marbles:
            if best_marble.get_best_lap_time() > marble.get_best_lap_time():
                best_marble = marble
        return best_marble

marbles = MarbleList()


racecontrolThread = RacecontrolThread(1, marbles)


# configuration
DEBUG = False

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
socketio = SocketIO(app)
racecontrolThread.start()



@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('table')
def table_broadcast():
    table(True)


@socketio.on('tableOnce')
def table_once():
    table(False)


def table(broadcast):
    marbles.marbles.sort(key=lambda marble: (len(marble.lap_times), 1 / marble.get_overall_time()), reverse=True)
    if len(marbles.marbles) > 0:
        time_first = marbles.get(0).get_overall_time()
        laps_first = marbles.get(0).get_number_of_laps()
    else:
        laps_first = 0
        time_first = 0
    json_marbles = []
    for i, marble in enumerate(marbles.marbles):
        has_best_lap = False
        if marble == marbles.get_marble_with_best_lap():
            has_best_lap = True
            best_lap_time = marble.get_best_lap_time()
        else:
            best_lap_time = marble.get_best_lap_time() - marbles.get_marble_with_best_lap().get_best_lap_time()
        json_marbles.append({'id': marble.id, 'name': marble.name, 'last_lap_time': marble.get_last_lap_time(),
                             'laps': marble.get_number_of_laps(), 'color': 'rgb' + str(marble.get_display_color()),
                             'best_lap_time': best_lap_time, 'overall_time': marble.get_overall_time(),
                             'difference': marble.get_time_difference(time_first, laps_first), 'position': i +1, 'has_best_lap': has_best_lap})
    data = {'marbles': json_marbles}
    with app.app_context():
        socketio.emit('table', data, broadcast=broadcast)
    # return render_template('table.html', marbles=marbles, time_first=time_first)


@socketio.on('registerMarbles')
def register_marble():
    racecontrolThread.setRegistering(True)
    racecontrolThread.setRacing(False)
    emit('status', {'status': 'Registering'}, broadcast=True)


@socketio.on('endRegisterMarbles')
def register_marble():
    racecontrolThread.setRegistering(False)
    racecontrolThread.setRacing(False)
    emit('status', {'status': 'Registering stopped'}, broadcast=True)


@socketio.on('startRace')
def start_race():
    racecontrolThread.setRegistering(False)
    racecontrolThread.setRacing(True)
    emit('status', {'status': 'Started'}, broadcast=True)


@socketio.on('stopRace')
def stop_race():
    racecontrolThread.setRegistering(False)
    racecontrolThread.setRacing(False)
    emit('status', {'status': 'Stopped'}, broadcast=True)


@socketio.on('resetRace')
def reset_race():
    racecontrolThread.setRegistering(False)
    racecontrolThread.setRacing(False)
    for marble in marbles.marbles:
        marble.reset_marble()
    marbles.broadcast()
    emit('status', {'status': 'Race Reset'}, broadcast=True)

@socketio.on('changeName')
def change_name(data):
    marble = marbles.get_by_id(data['id'])
    if marble:
        marble.name = data['name']





marble = Marble(1, (123,45,23))
marble.lap_times.append(162.1234)
marble.lap_times.append(85.71789240837097)

marble2 = Marble(2, (0,255,0))
marble2.lap_times.append(162.1234)
marble2.lap_times.append(89.90212)

marbles.append(marble)
marbles.append(marble2)






if __name__ == '__main__':
    socketio.run(app)

