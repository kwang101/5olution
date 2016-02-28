import socketio
import eventlet
import json
from flask import Flask
from datetime import datetime as date
from datetime import timedelta
import thread
from colour import get_bus, register_item, item_is_locked_in

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
        if isinstance(obj, Colour):
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
items = {"test": Item("test", Colour(123, 123, 123)), "test2" : Item("test2", Colour(55, 111, 222))}
schedule = {}
active_schedule = {}
bus = get_bus()

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
    colour = register_item(bus)
    items[item_name] = Item(item_name, colour)
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
        schedule[day] = schedule.get(day, [])
        schedule[day].append(time_period)

def emit_schedules():

    def format_schedules(schedules):
        return [{'start_time': start_time, 'end_time': end_time, 'item_name': item_name} for start_time, end_time, item_name in schedules]
    formatted_schedule = {day: format_schedules(schedule) for day, schedule in schedule.items()}
    sio.emit('schedules', json.dumps(schedule, cls=MessageEncoder))

def emit_error(error_message):
    sio.emit('errors', json.dumps({"Message": error_message}, cls=MessageEncoder))

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


def remove_from_schedule(timespan, schedule):
    for day, time_period in timespan.items():
        schedule[day].remove(time_period)

def parse_alarm_payload(data):
    data = json.loads(data)
    timespan = {day_name : (day['start_time'], day['duration'], day['item_name']) for day_name, day in data['days'].items()}
    return format_timespan(timespan)

@sio.on('create_alarm')
def create_alarm(sid, data):
    timespans = parse_alarm_payload(data)
    if is_compatible_schedule(timespans, schedule):
        for timespan in timespans:
            insert_timespan_into_schedule(timespan, schedule)
        emit_schedules()
    else:
        emit_error("The alarm you've inserted overlaps with another alarm already scheduled.")

@sio.on('activate_alarm')
def activate_alarm(sid, data):
    timespans = parse_alarm_payload(data)
    for timespan in timespans:
        insert_timespan_into_schedule(timespan, active_schedule)

@sio.on('deactivate_alarm')
def deactivate_alarm(sid, data):
    timespans = parse_alarm_payload(data)
    for timespan in timespans:
        remove_from_schedule(timespan, active_schedule)

@sio.on('remove_alarm')
def remove_alarm(sid, data):
    timespans = parse_alarm_payload(data)
    for timespan in timespans:
        remove_from_schedule(timespan, schedule)

def check_alarms():
    while True:
        for day, timespans in active_schedule.items():
            if date.today().strftime("%A").lower() == day:
                current_time = date.now().time()
                minutes = current_time.hour() * 60 + current_time.minute()
                for start_time, duration, item_name in timespans:
                    if item_is_locked_in(bus, items[item_name].colour, date.now() + timedelta(minutes = duration)):
                        sio.emit('stop_alarm', None)
                    elif start_time - minutes <= 4 and start_time - minutes > 0:
                        sio.emit('warning', {"item_name": item_name})
                    elif start_time - minutes < 0:
                        sio.emit('start_alarm', None)

def createProcessingThread():
    thread.start_new_thread(check_alarms)

def initialize_server():
    app = Flask(__name__)
    app = socketio.Middleware(sio, app)
    createProcessingThread()
    server = eventlet.listen(('0.0.0.0', 8083))
    eventlet.wsgi.server(server, app)

def test_create_alarm():
    data = '{"days": {"monday": {"start_time": 1023, "duration": 500, "item_name": "phone"}}}'
    create_alarm(None, data)
    data2 = '{"days": {"monday": {"start_time": 900, "duration": 300, "item_name": "laptop"}}}'
    create_alarm(None, data2)
    data3 = '{"days": {"tuesday": {"start_time": 2, "duration": 300, "item_name": "laptop"}}}'
    create_alarm(None, data3)
    assert(len(schedule) == 2)

def test_activate_alarm():
    data = '{"days": {"monday": {"start_time": 1023, "duration": 500, "item_name": "phone"}}}'
    activate_alarm(None, data)
    check_alarms()
    assert(len(active_schedule) == 2)

def test_deactivate_alarm():
    data = '{"days": {"monday": {"start_time": 1023, "duration": 500, "item_name": "phone"}}}'
    deactivate_alarm(None, data)
    assert(len(active_schedule['monday']) == 0)
    activate_alarm(None, data)
    assert(len(active_schedule['monday']) == 1)
    assert(len(active_schedule['tuesday']) == 1)

if __name__ == '__main__':
    test_create_alarm()
    test_activate_alarm()
    test_deactivate_alarm()
    initialize_server()
