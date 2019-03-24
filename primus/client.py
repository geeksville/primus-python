

import sys
import logging
import engineio


class PrimusClient:
    """Client nub for talking to primus servers"""

    def __init__(self):
        """Constructor"""
        eio = engineio.Client()
        self.eio = eio

        @eio.on('connect')
        def on_connect():
            print('connection established')

        @eio.on('message')
        def on_message(data):
            print('message received with ', data)
            eio.send({'response': 'my response'})

        @eio.on('disconnect')
        def on_disconnect():
            print('disconnected from server')

    def connect(self, server):
        self.eio.connect(server)
        self.eio.wait()
