import tornado.ioloop
import tornado.web
import urllib, urllib2
import os, sys, json, xmpp, random, string
import threading, time

API_KEY = 'API_KEY'                                           
register_ids = []

#GOOGLE SERVER
SERVER = 'gcm.googleapis.com'
PORT = 5235

class MainHandler(tornado.web.RequestHandler):
    def get(self): 
        self.render("index.html", title="GCM Portal", items=register_ids)

    # Handler for method post
    def post(self):
        global register_ids
        reg_id = self.get_argument("reg_id", default=None)
        message = self.get_argument("message", default=None)
        attributes = self.request.arguments
        print 'attrubutes:'
        print '\n'.join(attributes)
        delete_ids = self.get_arguments("delete_id")
        send_ids = self.get_arguments("send_id")

        if reg_id is not None:
            register_ids.append(self.get_argument("reg_id"))
   

#        if message is not None:
#            reg_id = register_ids[0]
#            send_queue.append({'to': reg_id,
#                           'message_id': 'reg_id',
#                           'data': {'message_destination': 'RegId',
#                                    'message': message 
#                           }
#                          })


        if delete_ids is not None:
            print 'delete_ids method:'
            print '\n'.join(delete_ids)
            for id in delete_ids:
                register_ids.remove(id)
        
        if send_ids is not None:
            print 'send_ids method:'
            for id in send_ids:
                send_queue.append({'to': id,
                           'message_id': 'reg_id',
                           'data': {'message_destination': 'RegId',
                                    'message': message 
                           }
                          })


        self.render("index.html", title="GCM Portal", items=register_ids)


        #if request.get('reg_id'):
        #    self.write(request.get('reg_id'))

# Register device -> curl -H "Content-Type: application/json" -X POST --data '{"reg_id":<register_id>}' http://localhost:8888/register
class RegisterHandler(tornado.web.RequestHandler):
    def post(self):
        global register_ids
        response_data = json.loads(self.request.body)
        if response_data.has_key('reg_id'):
            reg_id = response_data['reg_id']
            register_ids.append(reg_id)
            self.write(Message("Registred ID",reg_id).json())

# Show all registred devices curl -H "Content-Type: application/json" -X POST http://localhost:8888/ids
class IdsHandler(tornado.web.RequestHandler):
    def post(self):
        global register_ids
        self.write(Message("Registred Ids", register_ids).json());

# Show all registred devices curl -H "Content-Type: application/json" -X POST --data '{"reg_id":<register_id>}' http://localhost:8888/delete
class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        global register_ids
        response_data = json.loads(self.request.body)
        if response_data.has_key('reg_id'):
            delete_id = response_data['reg_id']
            if delete_id in register_ids: 
                register_ids.remove(delete_id)
                self.write(Message("delete reg_id", delete_id).json())
            else: 
                self.write(Message("reg_id not registred", delete_id).json())

class SendHandler(tornado.web.RequestHandler):
    def post(self):
        global API_KEY
        global register_ids

        msg = ""
        response_data = json.loads(self.request.body)
        if response_data.has_key('msg'):
            msg = response_data['msg']

        reg_id_list = None

        if reg_id_list is None:
            sys.stderr.write('Sending message to all registered devices\n')
            reg_id_list = list(register_ids)

        self.write(Message(msg, reg_id_list[0]).json())
        send_queue.append({'to': reg_id_list[0],
                           'message_id': 'reg_id',
                           'data': {'message_destination': 'RegId',
                                    'message': msg 
                           }
                          })
'''
        data = {
            'registration_ids' : reg_id_list,
            'data' : {
                    'msg' : msg
                    }
            }

        print 'data -> ' + json.dumps(data)
        headers = {
            'Content-Type' : 'application/json',
            'Authorization' : 'key=' + API_KEY
        }

        print 'headers -> ' + json.dumps(headers)

        url = 'https://android.googleapis.com/gcm/send'
        request = urllib2.Request(url, json.dumps(data), headers)

        try:
            response = urllib2.urlopen(request)
            json_string = response.read()
            json_response = json.loads(json_string)
            self.write(json_response)
            #self.send_response(200)
            #self.send_header('Content-type', 'text/html')
            #self.end_headers()
            #self.wfile.write(self.make_gcm_summary(data, response))
            return
        except urllib2.HTTPError, e:
            print e.code
            print e.read()

        return
'''

class Message:
    error = False
    message = ""
    reg_id = ""
    ids = []
    def __init__(self):
        self.error = False

    def __init__(self, message, reg_id, error=False):
        self.error = error
        self.message = message
        self.reg_id = reg_id

    def json(self):
        return json.dumps(self.__dict__)

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "./logs"),
}

application = tornado.web.Application([(r"/", MainHandler),
                                       (r"/register", RegisterHandler),
                                       (r"/ids", IdsHandler),
                                       (r"/send", SendHandler),
                                       (r"/delete", DeleteHandler),
                                       (r"/logs/(.*)", 
                                           tornado.web.StaticFileHandler,
                                           dict(path=settings['static_path'])),

                                    ], **settings)

class HTTPServerThread(threading.Thread):
    def run(self):
        print 'Tornado Thread ... [OK]'
        application.listen(8888)
        time.sleep(1)
        tornado.ioloop.IOLoop.instance().start()

# SERVER XMPP
# Project Number
USERNAME = "PROJECT NUMBER"
PASSWORD = API_KEY

unacked_messages_quota = 100
send_queue = []

def message_callback(session, message):
    global unacked_messages_quota
    gcm = message.getTags('gcm')
    if gcm:
        gcm_json = gcm[0].getData()
        msg = json.loads(gcm_json)
        if not msg.has_key('message_type'):
            # Acknowledge the incoming message immediately.
            send({'to': msg['from'], 'message_type': 'ack', 'message_id': msg['message_id']})
        # Queue a response back to the server.
        #if msg.has_key('from'):
            # Send a dummy echo response back to the app that sent the upstream message.
            # send_queue.append({'to': msg['from'],
            #                      'message_id': random_id(),
            #                      'data': {'pong': 1}})
    
    elif msg['message_type'] == 'ack' or msg['message_type'] == 'nack':
                unacked_messages_quota += 1

def send(json_dict):
    template = ("<message><gcm xmlns='google:mobile:data'>{1}</gcm></message>")
    client.send(xmpp.protocol.Message(node=template.format(client.Bind.bound[0], json.dumps(json_dict))))

def flush_queued_messages():
    global unacked_messages_quota
    while len(send_queue) and unacked_messages_quota > 0:
        send(send_queue.pop(0))
        unacked_messages_quota -= 1

RUN_XMPP=True
client = xmpp.Client('gcm.googleapis.com', debug=['socket'])

class XMPPThread(threading.Thread):
    def run(self):
        print 'XMPP Thread run authentication...'
        global client
        client = xmpp.Client('gcm.googleapis.com', debug=['socket'])
        client.connect(server=(SERVER,PORT), secure=1, use_srv=False)
        auth = client.auth(USERNAME, PASSWORD)
        if not auth:
            print 'Authentication failed!'
            sys.exit(1)

        client.RegisterHandler('message', message_callback)
        print 'XMPP Thread ... [OK]'
        global RUN_XMPP
        while RUN_XMPP:
            client.Process(1)
            time.sleep(1)
            flush_queued_messages()

if __name__ == "__main__":
    try:
        web_thread = HTTPServerThread(name = 'HTTP Thread')
        web_thread.daemon = True
        web_thread.start()
        xmpp_thread = XMPPThread(name = 'XMPP Thread')
        xmpp_thread.daemon = True
        xmpp_thread.start()
        xmpp_thread.join(99999)
    except KeyboardInterrupt:
        print '----Ctrl-C----'
        RUN_XMPP=False
