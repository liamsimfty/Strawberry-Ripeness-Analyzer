from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from strawberry_ripeness_analyzer import WebStrawberryAnalyzer
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request harus dalam format JSON'
            }), 400

        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Data request kosong'
            }), 400
        
        if 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Tidak ada gambar yang dikirim'
            }), 400
        
        base64_image = data['image']
        
        if not base64_image:
            return jsonify({
                'success': False,
                'error': 'Data gambar kosong'
            }), 400

        # Validate base64 string format
        if not base64_image.startswith('data:image/'):
            return jsonify({
                'success': False,
                'error': 'Format gambar tidak valid. Gunakan format base64 dengan prefix data:image/'
            }), 400
        
        # Analyze the image
        result = analyzer.analyze_from_base64(base64_image)
        
        if 'error' in result:
            logger.error(f"Analysis error: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        if not result.get('color_stats'):
            return jsonify({
                'success': False,
                'error': 'Tidak dapat menganalisis warna stroberi. Pastikan gambar jelas dan stroberi terlihat dengan baik.'
            }), 400
        
        return jsonify({
            'success': True,
            'ripeness': result['ripeness'],
            'confidence': result['confidence'],
            'color_stats': result['color_stats']
        })
        
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Terjadi kesalahan server: {str(e)}'
        }), 500

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