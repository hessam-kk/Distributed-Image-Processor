from flask import Flask, request, send_file
from PIL import Image
import io

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['file']
    
    # Process Image
    image = Image.open(file.stream)
    image = image.convert("L") 
    
    # Return the actual image data immediately
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return send_file(img_byte_arr, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)