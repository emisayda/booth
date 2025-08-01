from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import os
import io # Import the io module

app = Flask(__name__)
CORS(app)

# Your API key is now stored securely on the backend
# Make sure you have set this environment variable where you host the app
REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

@app.route('/cutout', methods=['POST'])
def cutout():
    # --- No changes needed here ---
    if 'image' not in request.files:
        return "No image file provided", 400

    file = request.files['image']

    # --- No changes needed here ---
    # Forward the request to the remove.bg API with your key
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': file.read()}, # Use file.read() to send the file's content
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVE_BG_API_KEY},
    )

    # --- Code has been changed below ---
    if response.status_code == requests.codes.ok:
        # SUCCESS CASE:
        # Instead of saving the file to disk, send the image content
        # directly from memory. This is more efficient.
        return send_file(
            io.BytesIO(response.content),
            mimetype='image/png',
            as_attachment=True,
            download_name=f'processed_{file.filename}'
        )
    else:
        # ERROR CASE:
        # This is the critical fix. We now safely check if the response is JSON
        # before trying to parse it. This prevents the 500 error.
        try:
            # Try to parse the JSON error response from the API
            error_data = response.json()
            # The remove.bg API often nests errors in a list.
            error_message = error_data.get('errors', [{}])[0].get('title', 'Unknown API Error')
            return jsonify({"message": error_message}), response.status_code
        except ValueError:
            # If the response isn't JSON, return a generic error.
            return jsonify({"message": "An unexpected error occurred with the image processing service."}), 502 # 502 Bad Gateway is appropriate here

if __name__ == '__main__':
    # The 'temp' directory is no longer needed since we aren't saving files
    # os.makedirs('temp', exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
