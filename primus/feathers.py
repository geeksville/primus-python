
from .primus import PrimusClient
import logging


class FeathersClient(PrimusClient):
    """Client nub for talking to feathers servers"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.pendingCalls = {}  # a dict from callid to the promise

        # We convert raw messages into standard socket.io events, published using the name of event
        @self.on('message')
        def message_handler(msg):
            typ = msg['type']
            if typ == 0:
                # An event message
                data = msg['data']
                eventName = data[0]
                payload = data[1]
                logging.debug(f'Handling event: {eventName}')
                self.call_handler(eventName, payload)
            elif typ == 1:
                # A function result
                id = msg['id']
                data = msg['data']
                err = data[0]  # or None for success
                if err:
                    raise Exception(
                        f'Error returned from server {err.message}')
                result = data[1]  # only valid if !err
                logging.info(f'FIXME ignoring function result {result}')
            else:
                raise Exception('Unexpected message type')

    def serverAsync(self, *args):
        """Call a function on our server (and return the ID of that call)"""
        self.callid = self.callid + 1
        msg = {
            'id': self.callid,
            'type': 0,
            'data': args
        }
        logging.info(f'calling server function {msg}')
        self.ws.emit(json.dumps(msg))
        self.pendingCalls[msg.id] = "FIXME-need something to wait on"
        return msg.id

    def serverSync(self, *args):
        """Call a function on the server and then wait for a response"""
        id = self.serverAsync(*args)

    def serverGet(self, service, id, options={}):
        """Get a record from a feathers service"""
        return self.serverSync(service, 'get', id, options)

    def serverUpdate(self, service, id, payload, options={}):
        """Update a record on a feathers service"""
        return self.serverSync(service, 'update', id, payload, options)

    def serverPatch(self, service, id, payload, options={}):
        """Patch a record on a feathers service"""
        return self.serverSync(service, 'patch', id, payload, options)

    def serverRemove(self, service, id, options={}):
        """Remove a record from a feathers service"""
        return self.serverSync(service, 'remove', id, options)

    def serverFind(self, service, query, options={}):
        """Find records from a feathers service"""
        return self.serverSync(service, 'find', query, options)


def serviceEventName(service, method="patched"):
    """Generate the right event name to listen for operations on the service"""
    return f"{service} {method}"


appName = "joyframe"


class EZDeviceFeathers(FeathersClient):
    """Client nub for talking to EZDevice server"""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.callid = 0

        @self.on(serviceEventName('ezdevs', f'event:{appName}'))
        def devevent_handler(msg):
            id = msg["id"]
            name = msg["name"]
            self.call_handler('devevent', id, name)

        @self.on(serviceEventName('ezdevs', 'patched'))
        def patch_handler(msg):
            logging.debug('ignoring patch on dev')


"""
See https://docs.feathersjs.com/api/client/primus.html#direct-connection

# INFO:root:Received msg {'type': 0, 'data': ['ezdevs event:joyframe', {'name': 'one', 'id': 'JC30AEA4C29020'}]}


"primus::pong::1553458964359"	29	
13:22:44.359
{"type":0,"data":["ezdevs patched",{"_id":"JTB4E62DEA32B5","uuid":"7-24T2"}
"primus::ping::1553458994363"	29	
13:23:14.364
"primus::pong::1553458994363"	29	
13:23:14.364

up {"type":0,"data":["get","devices","f0001",{}],"id":1}	53	
19:24:03.051
up {"type":0,"data":["authenticate",{"strategy":"jwt","accessToken":"x.eyJ1c2VySWQiOiIyMjU1MTMiLCJpYXQiOjE1NTM0ODA2MDgsImV4cCI6MTU1MzU2NzAwOCwiYXVkIjoiaHR0cHM6Ly9lemRldmljZS5uZXQiLCJpc3MiOiJnZWVrc3ZpbGxlIiwic3ViIjoiYW5vbnltb3VzIiwianRpIjoiOWJlMDI0MTYtYWFjMS00NTEyLTgyZGQtOTczZDg0ODRhMmZkIn0.K22hflAYZrskLWwCn4fc3fUqXRHJEdLcy2xaV_Zx3SE"}],"id":2}	381	
19:24:03.052
down {"id":1,"type":1,"data":[{"name":"NotAuthenticated","message":"No auth token","code":401,"className":"not-authenticated","data":{},"errors":{}}]}	145	
19:24:03.070
down {"id":2,"type":1,"data":[null,{"accessToken":"x.eyJ1c2VySWQiOiIyMjU1MTMiLCJpYXQiOjE1NTM0ODA2NDMsImV4cCI6MTU1MzU2NzA0MywiYXVkIjoiaHR0cHM6Ly9lemRldmljZS5uZXQiLCJpc3MiOiJnZWVrc3ZpbGxlIiwic3ViIjoiYW5vbnltb3VzIiwianRpIjoiMzM4NDNjMWItYmMxOS00Y2MyLTkzMGItMDUzOTdkY2JlMTI5In0.3Rx-VqfcCwmoolsCAlxsxGNk0F3lGUDglcHEOBGBVp4"}]}	354	
19:24:03.073
up {"type":0,"data":["get","users","225513",{}],"id":3}	52	
19:24:03.075
down {"id":3,"type":1,"data":[null,{"githubId":"225513","updatedAt":"2019-03-24T20:28:05.990Z"}]}	301	


update call:
up: {"type":0,"data":["update","devices","f0001",{"_id":"f0001","schedule":"[{\"time\":\"11:26\",\"amount\":1}]"},{}],"id":4}	121	
down: {"id":4,"type":1,"data":[null,{"schedule":"[{\"time\":\"11:26\",\"amount\":1}]","_id":"f0001"}]}
"""
