import cv2
import numpy as np
from sklearn.cluster import KMeans
import base64
from PIL import Image
import io

class WebStrawberryAnalyzer:
    def __init__(self):
        self.lower_green = np.array([30, 10, 80])   # Hue 35, Saturasi lebih rendah, Value lebih tinggi
        self.upper_green = np.array([80, 150, 255]) # Range yang lebih sempit untuk hijau muda
        self.lower_red1 = np.array([0, 100, 100])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([160, 100, 100])
        self.upper_red2 = np.array([180, 255, 255])
    
    def process_base64_image(self, base64_string):
        """Convert base64 string to OpenCV image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            return opencv_image
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def preprocess_image(self, image):
        """Praproses gambar dengan blur untuk menghilangkan noise"""
        return cv2.GaussianBlur(image, (5, 5), 0)
    
    def segment_strawberry(self, image):
        """Segmentasi buah stroberi dari background"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Deteksi warna hijau muda untuk stroberi mentah
        green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        
        # Deteksi warna merah untuk stroberi matang
        red_mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        red_mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        # Gabungkan mask hijau dan merah
        combined_mask = cv2.bitwise_or(green_mask, red_mask)
        
        # Operasi morfologi untuk memperbaiki mask
        kernel = np.ones((5, 5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        segmented = cv2.bitwise_and(image, image, mask=combined_mask)
        
        # Hitung rasio piksel stroberi
        total_pixels = image.shape[0] * image.shape[1]
        strawberry_pixels = np.sum(combined_mask > 0)
        strawberry_ratio = strawberry_pixels / total_pixels
        
        if strawberry_ratio < 0.05:
            return None, combined_mask
            
        return segmented, combined_mask
    
    def analyze_ripeness(self, segmented, mask):
        """Analisis tingkat kematangan stroberi berdasarkan nilai HSV"""
        if segmented is None:
            return {
                "ripeness": "Tidak terdeteksi stroberi",
                "confidence": 0,
                "color_stats": None
            }
            
        hsv = cv2.cvtColor(segmented, cv2.COLOR_BGR2HSV)
        hsv_values = hsv[mask > 0]
        
        if hsv_values.size == 0:
            return {
                "ripeness": "Tidak terdeteksi stroberi",
                "confidence": 0,
                "color_stats": None
            }
            
        hsv_values = hsv_values.reshape(-1, 3)
        
        # Prevent empty cluster error
        if len(hsv_values) < 5:
            n_clusters = len(hsv_values)
        else:
            n_clusters = 5
            
        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
        kmeans.fit(hsv_values)
        dominant_colors = kmeans.cluster_centers_
        
        h_avg = np.mean(dominant_colors[:, 0])
        s_avg = np.mean(dominant_colors[:, 1])
        v_avg = np.mean(dominant_colors[:, 2])
        
        # Hitung rasio piksel hijau muda vs merah
        hsv = cv2.cvtColor(segmented, cv2.COLOR_BGR2HSV)
        green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        red_mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        red_mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        green_pixels = np.sum(green_mask > 0)
        red_pixels = np.sum(red_mask > 0)
        total_pixels = green_pixels + red_pixels
        
        color_ratio = {
            "light_green_ratio": green_pixels / total_pixels if total_pixels > 0 else 0,
            "red_ratio": red_pixels / total_pixels if total_pixels > 0 else 0
        }
        
        # Pastikan tidak ada NaN values
        color_ratio["light_green_ratio"] = max(0, min(1, color_ratio["light_green_ratio"]))
        color_ratio["red_ratio"] = max(0, min(1, color_ratio["red_ratio"]))
        
        # Normalisasi jika total melebihi 100%
        total_ratio = color_ratio["light_green_ratio"] + color_ratio["red_ratio"]
        if total_ratio > 1:
            color_ratio["light_green_ratio"] /= total_ratio
            color_ratio["red_ratio"] /= total_ratio
        
        color_stats = {
            "hue": float(h_avg) if not np.isnan(h_avg) else 0.0,
            "saturation": float(s_avg) if not np.isnan(s_avg) else 0.0,
            "value": float(v_avg) if not np.isnan(v_avg) else 0.0,
            "light_green_ratio": float(color_ratio["light_green_ratio"]) if not np.isnan(color_ratio["light_green_ratio"]) else 0.0,
            "red_ratio": float(color_ratio["red_ratio"]) if not np.isnan(color_ratio["red_ratio"]) else 0.0
        }
        
        # Logika kematangan untuk stroberi
        ripeness = "Tidak dapat ditentukan"
        confidence = 0
        
        if color_ratio["light_green_ratio"] > 0.7:
            ripeness = "Mentah (Hijau Muda)"
            confidence = min(95, color_ratio["light_green_ratio"] * 100)
        elif color_ratio["light_green_ratio"] > 0.3:
            ripeness = "Setengah Matang"
            confidence = 80
        elif s_avg > 200 and v_avg > 200 and color_ratio["red_ratio"] > 0.9:
            ripeness = "Sangat Matang"
            confidence = min(95, color_ratio["red_ratio"] * 100)
        elif s_avg > 150 and v_avg > 150 and color_ratio["red_ratio"] > 0.7:
            ripeness = "Matang"
            confidence = min(90, color_ratio["red_ratio"] * 100)
        elif color_ratio["red_ratio"] > 0.5:
            ripeness = "Setengah Matang"
            confidence = 75
        
        return {
            "ripeness": ripeness,
            "confidence": float(confidence),
            "color_stats": color_stats
        }
    
    def analyze_from_base64(self, base64_image):
        """Main analysis function for web interface"""
        try:
            # Convert base64 to OpenCV image
            image = self.process_base64_image(base64_image)
            if image is None:
                return {"error": "Gagal memproses gambar"}
            
            # Preprocess
            preprocessed = self.preprocess_image(image)
            
            # Segment
            segmented, mask = self.segment_strawberry(preprocessed)
            
            # Analyze
            result = self.analyze_ripeness(segmented, mask)
            
            return result
            
        except Exception as e:
            return {"error": f"Error dalam analisis: {str(e)}"}