from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import math
from datetime import datetime

# app instance
app = Flask(__name__)
CORS(app)

load_dotenv() # get environment variables

API_KEY = os.getenv('API_KEY') # get the API_KEY from the .env file
LAT = os.getenv('LAT') # get the LAT from the .env file
LON = os.getenv('LON') # get the LON from the .env file
MAX_DISTANCE = os.getenv('MAX_DISTANCE') # get the MAX_DISTANCE

def get_current_time():
    return datetime.now().timestamp()


# api/test
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Hello from the server!',
    })

# api/departures
@app.route('/api/departures', methods=['GET'])
def departures():

    payload = {
        'lat': LAT,
        'lon': LON,
        'max_distance' : MAX_DISTANCE
    }

    headers = {
        'apiKey' : API_KEY
    }

    # get the data from the API
    response = requests.get('https://external.transitapp.com/v3/public/nearby_routes', headers=headers, params=payload)

    # return the data
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True, port=8080) # run the server in debug mode