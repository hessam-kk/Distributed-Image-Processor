from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageFilter
import io
import time
import socket 

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_image():
    # Simulate heavy work
    time.sleep(2)
    
    file = request.files['file']
    
    # 1. Capture Pod Name (Hostname)
    pod_name = socket.gethostname()

    # 2. Process
    image = Image.open(file.stream)
    image = image.filter(ImageFilter.BLUR)
    
    # 3. Return Image AND Pod Name in headers
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return send_file(
        img_byte_arr, 
        mimetype='image/png',
        # Add custom header so we can see who did the work
        download_name=pod_name 
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)