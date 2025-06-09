from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from strawberry_ripeness_analyzer import WebStrawberryAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize analyzer
analyzer = WebStrawberryAnalyzer()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_strawberry():
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        base64_image = data['image']
        
        # Analyze the image
        result = analyzer.analyze_from_base64(base64_image)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'ripeness': result['ripeness'],
            'confidence': result['confidence'],
            'color_stats': result['color_stats']
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Starting Strawberry Analyzer Server...")
    print("Access the web interface at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)