import json
import os
from datetime import time
from imghdr import tests
from os import write
from time import sleep
from PyPDF2 import PdfWriter
import task_generator
import auto_pull_math
import selenium_handler
import pdf_extractor

from flask import jsonify, Flask, request
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app, origins="*")

# @app.route('/api/users', methods=['GET'])
# def users():
#     return jsonify(
#         {
#             'users' : [
#                 'arpan',
#                 'zach',
#                 'jessie'
#             ]
#         }
#     )

school = ''
@app.route('/api/set_school', methods=['POST'])
def set_school():
  request_data = request.get_json()
  global school
  school = request_data['name']
  return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/api/upload', methods=['POST'])
def upload_file():
  print("test")
  # Check if the request contains a file
  if 'file' not in request.files:
    return jsonify({'error': 'No file part in the request'}), 400

  file = request.files['file']

  # Check if the file has a valid name
  if file.filename == '':
    return jsonify({'error': 'No file selected'}), 400

  # Save the file to the UPLOAD_FOLDER
  filepath = os.path.join('./', "parse.pdf")
  file.save(filepath)
  pdf_extractor.parse()

  return jsonify({'message': 'File uploaded successfully', 'file_path': filepath}), 200


@app.route('/api/login', methods=['POST'])
def sso_login():
  global school
  request_data = request.get_json()
  if not selenium_handler.init(request_data['user'], request_data['pass'], school):
    return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
  return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/api/get_school', methods=['GET'])
def get_school():
  global school
  return jsonify(
    {
      'school' : school
    }
  )




if __name__ == '__main__':
    app.run(debug=True, port=8080)
    # main()
