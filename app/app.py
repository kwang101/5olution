import websockets as ws
import asyncio
import json
from enum import Enum


#commands = {'register': }
connections = set()
alarms = {}

async def recv_command(websocket, path):
    global connections
    try:
        while True:
            data = await websocket.recv()
            connections.add(websocket)
            response_data = parse_and_handle_data(data)
    finally:
        connections.remove(websocket)

def parse_and_handle_data(data):
    json = json.loads(data)
    response = {}
    if json['type'] == 'register':
        register_new_item()
        response['type'] = 'server_response'
        response['is_successful'] = True
    elif json['type'] == 'activate_alarm':
        alarm_id = json['alarm_id']


def register_new_item():
    pass

def activate_alarm(alarm_id, active_until):
    alarms[alarm_id] = {'status': 'active', 'active_until': active_until}

def deactivate_alarm(alarm_id):
    alarms.pop(alarm_id, None)

def initialize_server():
    start_server = ws.serve(recv_command, '127.0.0.1', 8080)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    initialize_server()
