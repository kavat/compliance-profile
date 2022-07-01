import json
import shutil
import config
import zlib
import string
import random

from inspec import get_inspec_analysis
from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)

@app.route('/')
def hello_world():
    return { "status" : True }

@app.route('/run_profile', methods=["POST"])
def run_profile():
  try:
    host = request.json["host"]
    username = request.json["username"]
    password = request.json["password"]
    profile = request.json["profile"]
    os = request.json["os"]
    return get_inspec_analysis(id_generator, username, password, host, profile, os)
  except Exception as e:
    print("Errore per {}: {}".format(host, str(e)))
    return { "status": False, "message": str(e) } 

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
  app.run(debug = config.WEB_DEBUG,
          host  = config.WEB_HOST,
          port  = config.WEB_PORT,
          threaded=True)
