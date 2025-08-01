from flask import Flask, request, send_file
from flask_cors import CORS
import requests # Import the requests library
import os

app = Flask(__name__)
CORS(app)

# Your API key is now stored securely on the backend
REMOVE_BG_API_KEY = "dDZPnYHqTaK5jGK7qmCgqodL"

@app.route('/cutout', methods=['POST'])
def cutout():
    if 'image' not in request.files:
        return "No image file provided", 400

    file = request.files['image']

    # Forward the request to the remove.bg API with your key
    response = requests.post(
        'https://api.remove.bg/v1/removebg',
        files={'image_file': file},
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVE_BG_API_KEY},
    )

    if response.status_code == requests.codes.ok:
        # If successful, save the result and send it back to the frontend
        output_path = f'temp/processed_{file.filename}.png'
        with open(output_path, 'wb') as out:
            out.write(response.content)
        return send_file(output_path, mimetype='image/png')
    else:
        # If there's an error, forward the error message from the API
        return response.json(), response.status_code

if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
