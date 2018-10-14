# import redis
# from gevent import monkey
# monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
# db = redis.StrictRedis('localhost', 6379, 0)
socketio = SocketIO(app)

@app.route('/localhost')
def main():
	print('logger is working')
	return render_template('main.html')


@socketio.on('message', namespace='/localhost')
def handle_message(message):
    app.logger.info('received message: ' + message)

@socketio.on('json',namespace='/localhost')
def handle_json(json):
    app.logger.info('received json: ' + str(json))

@socketio.on('my event')
def handle_my_custom_event(json):
    print('my event', json)
    app.logger.info('received json: ' + str(json))
    return 'event test', 0

@socketio.on('my event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('my custom event', json)
    app.logger.info('received json with namespace /test: ' + str(json))
    return 'event test', 1

# @socketio.on('connect')
# def ws_conn():
# 	c = db.incr('user_count')
# 	print('connecting', c)
# 	socketio.emit('msg', {'count': c})
# 
# 
# @socketio.on('disconnect')
# def ws_disconn():
#         c = db.decr('user_count')
# 	print('disconnecting', c)
#         socketio.emit('msg', {'count': c})


if __name__ == '__main__':
	socketio.run(app, debug=True)
 
# import logging
# import tornado
# from flask import Flask, render_template
# from tornado.web import FallbackHandler
# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop
# from tornado.websocket import WebSocketHandler
# 
# from data import Data
# 
# app = Flask(__name__)
# app.config['SECRET_KEY'] = '1234567'
# 
# @app.route('/')
# def index():
#     return render_template('index.html')
# 
# def send_message(message):
#     for handler in ChatSocketHandler.socket_handlers:
#         try:
#             data = Data()
#             result = data.get_buy_price()
#             handler.write_message(message + '\' price is ' + str(result))
#         except:
#             logging.error('Error sending message', exc_info=True)
# 
# 
# class ChatSocketHandler(WebSocketHandler):
#     socket_handlers = set()
#     def open(self):
#         ChatSocketHandler.socket_handlers.add(self)
#         send_message('A new user has entered the Coinbase lobby.')
# 
#     def on_close(self):
#         ChatSocketHandler.socket_handlers.remove(self)
#         send_message('A user has left the Coinbase lobby.')
# 
#     def on_message(self, message):
#         send_message(message)
# 
# 
# if __name__ == '__main__':
#     applications = tornado.web.Application([# order matters! otherwise, everytying will go to flask server.
#                                             (r'/websocket', ChatSocketHandler),
#                                             (r'/', FallbackHandler, dict(fallback=WSGIContainer(app))),
#                                             ])
#     http_server = HTTPServer(applications)
#     http_server.listen(5000)
#     IOLoop.instance().start()
