from digitsfinder import create_app, db
#from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    #app.run(debug=True)
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
