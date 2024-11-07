from flask import Flask, request, jsonify
from flask_cors import CORS

# app instance
app = Flask(__name__)
CORS(app)

# api/test route
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Hello World!',
        'people' : ['Alice', 'Bob', 'Charlie']
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080) # run the server in debug mode