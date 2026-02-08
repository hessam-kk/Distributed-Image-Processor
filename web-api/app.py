import requests
from flask import Flask, request, jsonify, send_file
import os
import io
import redis

app = Flask(__name__)

# Config
BW_SERVICE_URL = os.getenv('BW_URL', 'http://bw-service:5001')
BLUR_SERVICE_URL = os.getenv('BLUR_URL', 'http://blur-service:5001')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')

# Connect to Redis for reading images
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    effect = request.form.get('effect', 'blur')
    
    # 1. Router Logic
    target_url = BLUR_SERVICE_URL if effect == 'blur' else BW_SERVICE_URL
    
    # 2. Forward Request
    try:
        files = {'file': (file.filename, file.read(), file.content_type)}
        response = requests.post(f"{target_url}/process", files=files)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image/<id>', methods=['GET'])
def get_image(id):
    # 3. Fetch from Redis and return as actual image
    img_data = r.get(id)
    if not img_data:
        return jsonify({"error": "Image not found"}), 404
        
    return send_file(io.BytesIO(img_data), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)