import logging
import tornado
from flask import Flask, render_template
from tornado.web import FallbackHandler
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from data import Data

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567'

@app.route('/')
def index():
    return render_template('index.html')

def send_message(message):
    for handler in ChatSocketHandler.socket_handlers:
        try:
            data = Data()
            result = data.get_buy_price()
            handler.write_message(message + '\' price is ' + str(result))
        except:
            logging.error('Error sending message', exc_info=True)


class ChatSocketHandler(WebSocketHandler):
    socket_handlers = set()
    def open(self):
        ChatSocketHandler.socket_handlers.add(self)
        send_message('A new user has entered the Coinbase lobby.')

    def on_close(self):
        ChatSocketHandler.socket_handlers.remove(self)
        send_message('A user has left the Coinbase lobby.')

    def on_message(self, message):
        send_message(message)


if __name__ == '__main__':
    applications = tornado.web.Application([# order matters! otherwise, everytying will go to flask server.
                                            (r'/websocket', ChatSocketHandler),
                                            (r'/', FallbackHandler, dict(fallback=WSGIContainer(app))),
                                            ])
    http_server = HTTPServer(applications)
    http_server.listen(5000)
    IOLoop.instance().start()