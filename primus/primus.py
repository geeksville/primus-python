

import logging
import websockets
import asyncio
import re
import json

pingPattern = re.compile("\"primus::ping::(.+)\"")


class EventPublisher:
    """A utility baseclass that adds easy by name event publishing"""

    def __init__(self):
        """Constructor"""
        self.handlers = {}

    def on(self, event, handler=None):
        """Register an event handler.
        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param handler: The function that should be invoked to handle the
                        event. When this parameter is not given, the method
                        acts as a decorator for the handler function.
        Example usage::
            # as a decorator:
            @primus.on('connect')
            def connect_handler():
                print('Connected!')
            # as a method:
            def message_handler(msg):
                print('Received message: ', msg)
                primus.send( 'response')
            primus.on('message', message_handler)
        The ``'connect'`` event handler receives no arguments. The
        ``'message'`` handler and handlers for custom event names receive the
        message payload as only argument. Any values returned from a message
        handler will be passed to the client's acknowledgement callback
        function if it exists. The ``'disconnect'`` handler does not take
        arguments.
        """
        def set_handler(handler):
            logging.info(f'registering handler for {event}')
            self.handlers[event] = handler
            return handler

        if handler is None:
            return set_handler
        set_handler(handler)

    def call_handler(self, name, *args):
        """Call a particular handler name"""
        h = self.handlers.get(name)
        if h:
            h(*args)
        else:
            logging.info(f'No handler registered for {name} msg={ args }')


class PrimusClient(EventPublisher):
    """Client nub for talking to primus servers"""

    def __init__(self):
        """Constructor"""
        super().__init__()

    def connect(self, server):
        self.ws = websockets.connect(server)

        async def listener():
            async with self.ws as ws:
                while True:
                    msg = await ws.recv()
                    logging.debug(f"< {msg}")
                    ping = pingPattern.match(msg)
                    if ping:
                        logging.info("Sending pong")
                        await ws.send(f"primus::pong::{ping.group(1)}")
                    else:
                        asJson = json.loads(msg)
                        logging.debug(f"Received msg {asJson}")
                        self.call_handler('message', asJson)

        asyncio.get_event_loop().run_until_complete(listener())

    def close(self):
        """Shut down our connection to the server"""
        # await asyncio.wait({self.task})
        #


"""
See https://docs.feathersjs.com/api/client/primus.html#direct-connection

"primus::pong::1553458964359"	29	
13:22:44.359
{"type":0,"data":["ezdevs patched",{"_id":"JTB4E62DEA32B5","uuid":"7e165b3d-ff29-4b73-be7c-85b3944b3cea","application":"joyframe","createdAt":"2019-03-13T02:53:33.960Z","ipAddress":"99.152.116.156","updatedAt":"2019-03-24T20:22:44.811Z","contactAt":"2019-03-24T19:19:44.692Z","status":"online","firmwareVersion":"V0.1.7-34","firmwareNum":34,"netinfo":"geeksville","display":{"html":"<html>\n <head>\n \t<style>\n p { font-size: 6vw; font-weight: bold; font-smooth: never; -webkit-font-smoothing: none }\n body { \n margin: 0 !important;\n padding: 0 !important;\n }\n \t</style>\n </head>\n <body>\n <div id=\"body\"> <p>Q: How many surrealists does it take to change a light bulb?<p><p>A: To get to the other side.<p> </div>\n </body></html>","options":{"allowDithering":false},"mode":"forever"},"hasBootScreen":true,"function":{"pending":{"1o1g6ft":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/1o1g6ft.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689212&Signature=sQbETxlBGuqxsDPVt5hGTx1Nl8Q%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/1o1g6ft.jpg","id":"1o1g6ft","time":"2019-03-14T21:33:32.747Z"},"1913fqp":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/1913fqp.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689229&Signature=sOfyNGl1WMdrTSWRlomDsZ3MeLo%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/1913fqp.jpg","id":"1913fqp","time":"2019-03-14T21:33:49.308Z"},"1m3zxix":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/1m3zxix.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689692&Signature=79z8AWeXc6QfgEE3wsWQsLqkPDM%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/1m3zxix.jpg","id":"1m3zxix","time":"2019-03-14T21:41:32.465Z"},"m65vdc":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/m65vdc.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689693&Signature=bTUJHMRQRKVBANFAUIYhqaJ5Fnc%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/m65vdc.jpg","id":"m65vdc","time":"2019-03-14T21:41:33.241Z"}},"result":{"wxu9vd":{"value":"200","time":"2019-03-22T01:40:56.095Z"}}},"camera":{"image":"https://joyblobs.s3.us-west-2.amazonaws.com/wxu9vd.jpg"},"debugImage":"data:image/png;base64,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"}]}	5046	
13:22:44.819
{"type":0,"data":["ezdevs patched",{"_id":"JTB4E62DEA32B5","uuid":"7e165b3d-ff29-4b73-be7c-85b3944b3cea","application":"joyframe","createdAt":"2019-03-13T02:53:33.960Z","ipAddress":"99.152.116.156","updatedAt":"2019-03-24T20:22:44.894Z","contactAt":"2019-03-24T19:19:44.692Z","status":"online","firmwareVersion":"V0.1.7-34","firmwareNum":34,"netinfo":"geeksville","display":{"html":"<html>\n <head>\n \t<style>\n p { font-size: 6vw; font-weight: bold; font-smooth: never; -webkit-font-smoothing: none }\n body { \n margin: 0 !important;\n padding: 0 !important;\n }\n \t</style>\n </head>\n <body>\n <div id=\"body\"> <p>Q: How many surrealists does it take to change a light bulb?<p><p>A: To get to the other side.<p> </div>\n </body></html>","options":{"allowDithering":false},"mode":"forever"},"hasBootScreen":true,"function":{"pending":{"1o1g6ft":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/1o1g6ft.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689212&Signature=sQbETxlBGuqxsDPVt5hGTx1Nl8Q%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/1o1g6ft.jpg","id":"1o1g6ft","time":"2019-03-14T21:33:32.747Z"},"1913fqp":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/1913fqp.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689229&Signature=sOfyNGl1WMdrTSWRlomDsZ3MeLo%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/1913fqp.jpg","id":"1913fqp","time":"2019-03-14T21:33:49.308Z"},"1m3zxix":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/1m3zxix.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689692&Signature=79z8AWeXc6QfgEE3wsWQsLqkPDM%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/1m3zxix.jpg","id":"1m3zxix","time":"2019-03-14T21:41:32.465Z"},"m65vdc":{"name":"snapshot","arg":"http://joyblobs.s3.us-west-2.amazonaws.com/m65vdc.jpg?AWSAccessKeyId=AKIAIEQUPES6MS3J6XVA&Content-Type=image%2Fjpeg&Expires=1552689693&Signature=bTUJHMRQRKVBANFAUIYhqaJ5Fnc%3D&x-amz-acl=public-read","getURL":"https://joyblobs.s3.us-west-2.amazonaws.com/m65vdc.jpg","id":"m65vdc","time":"2019-03-14T21:41:33.241Z"}},"result":{"wxu9vd":{"value":"200","time":"2019-03-22T01:40:56.095Z"}}},"camera":{"image":"https://joyblobs.s3.us-west-2.amazonaws.com/wxu9vd.jpg"},"debugImage":"data:image/png;base64,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"}]}	4774	
13:22:44.898
"primus::ping::1553458994363"	29	
13:23:14.364
"primus::pong::1553458994363"	29	
13:23:14.364"""
