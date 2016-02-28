import socketio
import eventlet
import json
from enum import Enum
from flask import Flask

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

sio = socketio.Server()
connections = set()
alarms = {}
items = {"test": Item("test", "red"), "test2" : Item("test2", "pink")}

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
    print(sid)
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


def activate_alarm(alarm_id, active_until):
    alarms[alarm_id] = {'status': 'active', 'active_until': active_until}

def deactivate_alarm(alarm_id):
    alarms.pop(alarm_id, None)

def initialize_server():
    app = Flask(__name__)
    app = socketio.Middleware(sio, app)
    server = eventlet.listen(('0.0.0.0', 8081))
    eventlet.wsgi.server(server, app)

if __name__ == '__main__':
    initialize_server()
