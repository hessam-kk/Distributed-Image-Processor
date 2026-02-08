from flask import Flask, request, jsonify
from PIL import Image, ImageFilter
import io
import redis
import os
import uuid

app = Flask(__name__)
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')
r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['file']
    
    # Logic specific to Blur
    image = Image.open(file.stream)
    image = image.filter(ImageFilter.BLUR)
    
    # Save to Redis
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format or 'PNG')
    image_id = str(uuid.uuid4())
    r.set(image_id, img_byte_arr.getvalue())
    
    return jsonify({"id": image_id, "service": "blur-processor"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)