import socketio
import eventlet
import json
from flask import Flask
from datetime import datetime

class Item(object):
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour

class Alarm(object):
    def __init__(self, item, start_time, end_time):
        self.item
    def toJSON(self, o):
        return json.dumps(self.__dict__)

class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            return obj.__dict__
        if isinstance(obj, Alarm):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)

next_day = {
    'monday': 'tuesday',
    'tuesday': 'wednesday',
    'wednesday': 'thursday',
    'thursday': 'friday',
    'friday': 'saturday',
    'saturday': 'sunday',
    'sunday': 'monday'
}

sio = socketio.Server()
connections = set()
alarms = {'id' : 0}
items = {"test": Item("test", "red"), "test2" : Item("test2", "pink")}
schedule = {}

#items = {"test" + str(i) : Item("test" + str(i), "colour" + str(i)) for i in range(5)}

def emit_items():
    sio.emit('items', json.dumps(list(items.values()), cls=MessageEncoder))

@sio.on('connect')
def connect(sid, data):
    global connections
    sio.emit('items', json.dumps(list(items.values()), cls=MessageEncoder), sid)
    connections.add(sid)

@sio.on('disconnect')
def connect(sid):
    global connections
    connections.remove(sid)

@sio.on('register')
def register_item(sid, data):
    registration_data = json.loads(data)
    item_name = registration_data['item_name']
    items[item_name] = Item(item_name, "test")
    emit_items()

@sio.on('unregister')
def unregister_item(sid, data):
    data = json.loads(data)
    items.pop(data['item_name'], None)
    emit_items()

@sio.on('get_items')
def get_items(sid, data):
    sio.emit('itemList', json.dumps(list(items.values()), cls=MessageEncoder))

def is_compatible_schedule(candidate_timespans, schedule):
    for candidate_timespan in candidate_timespans:
        for day, timespan in candidate_timespan.items():
            if day in schedule:
                candidate_start_time, candidate_end_time, _ = timespan
                for start_time, end_time, _ in schedule[day]:
                    if candidate_start_time < end_time and candidate_start_time > start_time:
                        return False
                    elif candidate_end_time > start_time and candidate_end_time < end_time:
                        return False
    return True


def insert_timespan_into_schedule(timespan, schedule):
    for day, time_period in timespan.items():
        schedule[day] = schedule.get(day, [time_period])

def emit_schedules():

    def format_schedules(schedules):
        return [{'start_time': start_time, 'end_time': end_time, 'item_name': item_name} for start_time, end_time, item_name in schedules]
    formatted_schedule = {day: format_schedules(schedule) for day, schedule in schedule.items()}
    sio.emit('schedules', json.dumps(schedule, cls=MessageEncoder))

def emit_error(error_message):
    sio.emit('errors', json.dumps({"Message": error_message}, cls=MessageEncoder))

@sio.on('create_alarm')
def create_alarm(sid, data):
    data = json.loads(data)
    candidate_timespan = {day_name : (day['start_time'], day['duration'], day['item_name']) for day_name, day in data['days'].items()}

    def format_timespan(timespan):
        timespans = []
        day = timespan.keys()[0]
        start_time, duration, item_name = timespan[day]
        if start_time + duration > 1440:
            timespans.append({
                 day : (start_time, 1440, item_name)
            })
            timespans.append({
                 next_day[day] : (0, start_time + duration - 1440, item_name)
            })
        else:
            timespans.append(timespan)
        return timespans

    timespans = format_timespan(candidate_timespan)

    if is_compatible_schedule(timespans, schedule):
        for timespan in timespans:
            insert_timespan_into_schedule(timespan, schedule)
        emit_schedules()
    else:
        emit_error("The alarm you've inserted overlaps with another alarm already scheduled.")

def activate_alarm(alarm_id, active_until):
    alarms[alarm_id] = {'status': 'active', 'active_until': active_until}

def deactivate_alarm(alarm_id):
    alarms.pop(alarm_id, None)

def initialize_server():
    app = Flask(__name__)
    app = socketio.Middleware(sio, app)
    server = eventlet.listen(('0.0.0.0', 8082))
    eventlet.wsgi.server(server, app)

def test_create_alarm():
    data = '{"days": {"monday": {"start_time": 1023, "duration": 500, "item_name": "phone"}}}'
    create_alarm(None, data)
    data2 = '{"days": {"monday": {"start_time": 900, "duration": 300, "item_name": "laptop"}}}'
    create_alarm(None, data2)
    data3 = '{"days": {"tuesday": {"start_time": 2, "duration": 300, "item_name": "laptop"}}}'
    create_alarm(None, data3)
    assert(len(schedule) == 2)

if __name__ == '__main__':
    test_create_alarm()
    initialize_server()
