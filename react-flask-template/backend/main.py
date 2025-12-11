from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/hello', methods=['GET'])
def hello():
    """
    Simple hello endpoint
    Returns a JSON response with a greeting message
    """
    return jsonify({
        'message': 'Hello from Flask Backend!',
        'status': 'success'
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Backend API'
    }), 200

if __name__ == '__main__':
    # Run Flask app on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)

