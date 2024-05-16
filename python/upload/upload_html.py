from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('/data/temp/', filename))  #文件保存的位置
        return jsonify({'message': 'File uploaded successfully!'})
    else:
        return jsonify({'message': 'No file uploaded!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006)
