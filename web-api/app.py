import requests
from flask import Flask, request, jsonify, send_file
import os
import io
import redis
import uuid

app = Flask(__name__)

# Config
BW_SERVICE_URL = os.getenv('BW_URL', 'http://bw-service:5001')
BLUR_SERVICE_URL = os.getenv('BLUR_URL', 'http://blur-service:5001')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')

# Connect to Redis
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    # Allow user to send list like "bw,blur" or just "bw"
    effects_str = request.form.get('effects', '') 
    effects_list = [e.strip() for e in effects_str.split(',') if e.strip()]

    # If no effects provided, default to blur
    if not effects_list:
        effects_list = ['blur']

    # Start with the original image data
    current_image_data = file.read()
    filename = file.filename

    worker_pod_name = "unknown"

    # Pipeline: Pass image through each requested service
    for effect in effects_list:
        target_url = None
        if effect == 'bw':
            target_url = f"{BW_SERVICE_URL}/process"
        elif effect == 'blur':
            target_url = f"{BLUR_SERVICE_URL}/process"
        
        if target_url:
            try:
                # Send the current state of the image to the next service
                files = {'file': (filename, current_image_data, 'image/png')}
                response = requests.post(target_url, files=files)
                
                if response.status_code == 200:
                    # Update our current image with the processed result
                    current_image_data = response.content
                    # CAPTURE THE POD NAME FROM WORKER HEADERS
                    # The worker sends 'Content-Disposition' or a custom header
                    if 'Content-Disposition' in response.headers:
                        # We stored pod name in 'filename=' part of header
                        worker_pod_name = response.headers.get('Content-Disposition')
                else:
                    return jsonify({"error": f"Service {effect} failed"}), 500
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    # Save the Final Result to Redis
    image_id = str(uuid.uuid4())
    r.set(image_id, current_image_data)

    return jsonify({
        "id": image_id, 
        "applied_effects": effects_list,
        "processed_by_pod": worker_pod_name,
        "view_url": f"/image/{image_id}"
    })

@app.route('/image/<id>', methods=['GET'])
def get_image(id):
    img_data = r.get(id)
    if not img_data:
        return jsonify({"error": "Image not found"}), 404
    return send_file(io.BytesIO(img_data), mimetype='image/png')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)