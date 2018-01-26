import logging
from logging.handlers import RotatingFileHandler
from threading import Thread

from flask import Flask, request

from src.datastore.factory import DatabaseFactory
from src.services import genderstats_service as service

app = Flask(__name__)


@app.route('/api/v1/genderstats', methods=['POST'])
def gender_count():
    if request is None or not request.json or not 'videoId' in request.json:
        app.logger.info('missing VideoId from request')
        return 'missing data', 400
    else:
        videoId = request.json['videoId']
        app.logger.info('start getting gender data fro video ' + videoId)
        job = Thread(target=service.detect_gender, args=(videoId, app.logger))
        job.setDaemon(True)
        job.start()
        return 'ok', 200


if __name__ == '__main__':
    database_service = DatabaseFactory().build().get_database_service()
    service.database_service = database_service
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler('../logfile.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(debug=True, port=5000)
