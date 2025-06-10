import cv2 # Mengimpor pustaka OpenCV untuk tugas-tugas visi komputer
import numpy as np # Mengimpor NumPy untuk operasi numerik, terutama manipulasi array
from sklearn.cluster import KMeans # Mengimpor KMeans untuk pengelompokan (clustering), digunakan di sini untuk menemukan warna dominan
import base64 # Mengimpor base64 untuk mengkodekan dan mendekode string base64
from PIL import Image # Mengimpor Image dari Pillow (PIL) untuk pemrosesan gambar
import io # Mengimpor io untuk menangani aliran byte

class WebStrawberryAnalyzer: # Mendefinisikan kelas bernama WebStrawberryAnalyzer untuk membungkus logika analisis stroberi
    def __init__(self): # Metode konstruktor untuk kelas, diinisialisasi saat objek dibuat
        self.lower_green = np.array([30, 50, 80]) # Mendefinisikan batas bawah untuk warna hijau muda dalam ruang warna HSV (Hue, Saturation, Value)
        self.upper_green = np.array([40, 150, 255]) # Mendefinisikan batas atas untuk warna hijau muda dalam ruang warna HSV
        self.lower_red1 = np.array([0, 100, 100]) # Mendefinisikan batas bawah pertama untuk warna merah dalam HSV (merah melingkar di HSV)
        self.upper_red1 = np.array([10, 255, 255]) # Mendefinisikan batas atas pertama untuk warna merah dalam HSV
        self.lower_red2 = np.array([160, 100, 100]) # Mendefinisikan batas bawah kedua untuk warna merah dalam HSV
        self.upper_red2 = np.array([180, 255, 255]) # Mendefinisikan batas atas kedua untuk warna merah dalam HSV
    
    def process_base64_image(self, base64_string): # Metode untuk mengubah string base64 menjadi gambar OpenCV
        """Konversi string base64 ke gambar OpenCV""" # Docstring menjelaskan tujuan metode
        try: # Memulai blok try untuk menangani potensi kesalahan selama pemrosesan gambar
            # Hapus prefiks URL data jika ada
            if ',' in base64_string: # Memeriksa apakah string base64 mengandung koma, khas untuk prefiks URL data (misalnya, "data:image/jpeg;base64,...")
                base64_string = base64_string.split(',')[1] # Jika ada koma, pisahkan string dan ambil bagian kedua (data base64 yang sebenarnya)
            
            # Dekode base64
            image_data = base64.b64decode(base64_string) # Mendekode string base64 menjadi byte
            image = Image.open(io.BytesIO(image_data)) # Membuka data gambar menggunakan Pillow dari aliran byte
            
            # Konversi ke format OpenCV
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) # Mengonversi gambar Pillow (RGB) menjadi array NumPy, lalu mengubah ruang warnanya menjadi BGR untuk OpenCV
            return opencv_image # Mengembalikan gambar yang kompatibel dengan OpenCV
        except Exception as e: # Menangkap pengecualian apa pun yang terjadi selama proses
            print(f"Error processing image: {e}") # Mencetak pesan kesalahan jika terjadi pengecualian
            return None # Mengembalikan None jika terjadi kesalahan

    def preprocess_image(self, image): # Metode untuk melakukan praproses gambar
        """Praproses gambar dengan blur untuk menghilangkan noise""" # Docstring menjelaskan tujuan metode
        return cv2.GaussianBlur(image, (5, 5), 0) # Menerapkan filter Gaussian blur ke gambar untuk mengurangi noise, menggunakan kernel 5x5

    def segment_strawberry(self, image): # Metode untuk melakukan segmentasi stroberi dari latar belakang
        """Segmentasi buah stroberi dari background""" # Docstring menjelaskan tujuan metode
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Mengonversi gambar BGR ke ruang warna HSV, yang lebih baik untuk segmentasi berbasis warna
        
        # Deteksi warna hijau muda untuk stroberi mentah
        green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green) # Membuat mask biner untuk warna hijau muda menggunakan rentang HSV yang telah ditentukan
        
        # Deteksi warna merah untuk stroberi matang
        red_mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1) # Membuat mask biner untuk rentang warna merah pertama
        red_mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2) # Membuat mask biner untuk rentang warna merah kedua
        red_mask = cv2.bitwise_or(red_mask1, red_mask2) # Menggabungkan dua mask merah menggunakan operasi bitwise OR
        
        # Gabungkan mask hijau dan merah
        combined_mask = cv2.bitwise_or(green_mask, red_mask) # Menggabungkan mask hijau dan merah untuk mendapatkan mask stroberi lengkap
        
        # Operasi morfologi untuk memperbaiki mask
        kernel = np.ones((5, 5), np.uint8) # Membuat kernel (elemen struktural) 5x5 untuk operasi morfologi
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel) # Menerapkan operasi morfologi penutupan (closing) untuk menutup lubang kecil dan menghubungkan objek-objek terdekat di mask
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel) # Menerapkan operasi morfologi pembukaan (opening) untuk menghilangkan objek kecil dan menghaluskan batas di mask
        
        segmented = cv2.bitwise_and(image, image, mask=combined_mask) # Menerapkan mask gabungan ke gambar asli untuk mendapatkan stroberi yang tersegmentasi (hanya piksel di dalam mask yang dipertahankan)
        
        # Hitung rasio piksel stroberi
        total_pixels = image.shape[0] * image.shape[1] # Menghitung jumlah total piksel dalam gambar
        strawberry_pixels = np.sum(combined_mask > 0) # Menghitung jumlah piksel dalam mask yang merupakan bagian dari stroberi (bukan nol)
        strawberry_ratio = strawberry_pixels / total_pixels # Menghitung rasio piksel stroberi terhadap total piksel gambar
        
        if strawberry_ratio < 0.05: # Jika stroberi menempati kurang dari 5% dari gambar
            return None, combined_mask # Mengembalikan None untuk gambar tersegmentasi, menunjukkan tidak ada stroberi yang signifikan terdeteksi
            
        return segmented, combined_mask # Mengembalikan gambar tersegmentasi dan mask gabungan

    def analyze_ripeness(self, segmented, mask): # Metode untuk menganalisis tingkat kematangan stroberi
        """Analisis tingkat kematangan stroberi berdasarkan nilai HSV""" # Docstring menjelaskan tujuan metode
        if segmented is None: # Memeriksa apakah tidak ada stroberi yang terdeteksi selama segmentasi
            return { # Mengembalikan kamus yang menunjukkan tidak ada deteksi stroberi
                "ripeness": "Tidak terdeteksi stroberi", # Status kematangan
                "confidence": 0, # Tingkat kepercayaan
                "color_stats": None # Tidak ada statistik warna
            }
            
        hsv = cv2.cvtColor(segmented, cv2.COLOR_BGR2HSV) # Mengonversi gambar tersegmentasi ke HSV
        hsv_values = hsv[mask > 0] # Mengekstrak hanya nilai HSV dari piksel di dalam mask stroberi
        
        if hsv_values.size == 0: # Memeriksa apakah tidak ada nilai HSV yang diekstrak (berarti tidak ada piksel stroberi)
            return { # Mengembalikan kamus yang menunjukkan tidak ada deteksi stroberi
                "ripeness": "Tidak terdeteksi stroberi",
                "confidence": 0,
                "color_stats": None
            }
            
        hsv_values = hsv_values.reshape(-1, 3) # Mengubah bentuk nilai HSV menjadi array 2D di mana setiap baris adalah piksel HSV [H, S, V]
        
        # Mencegah kesalahan kluster kosong
        if len(hsv_values) < 5: # Jika jumlah piksel stroberi kurang dari 5 (minimum untuk KMeans dengan n_clusters=5)
            n_clusters = len(hsv_values) # Mengatur jumlah kluster ke jumlah piksel sebenarnya untuk menghindari kesalahan
        else:
            n_clusters = 5 # Jika tidak, gunakan 5 kluster untuk KMeans
            
        kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42) # Menginisialisasi KMeans dengan jumlah kluster yang ditentukan, 10 inisialisasi, dan keadaan acak tetap untuk reproduksibilitas
        kmeans.fit(hsv_values) # Melatih KMeans pada nilai HSV untuk menemukan warna dominan
        dominant_colors = kmeans.cluster_centers_ # Mendapatkan centroid (nilai HSV rata-rata) dari kluster warna dominan
        
        h_avg = np.mean(dominant_colors[:, 0]) # Menghitung rata-rata Hue dari warna dominan
        s_avg = np.mean(dominant_colors[:, 1]) # Menghitung rata-rata Saturation dari warna dominan
        v_avg = np.mean(dominant_colors[:, 2]) # Menghitung rata-rata Value dari warna dominan
        
        # Hitung rasio piksel hijau muda vs merah
        hsv = cv2.cvtColor(segmented, cv2.COLOR_BGR2HSV) # Mengonversi gambar tersegmentasi ke HSV lagi (redundant jika sudah dilakukan, tetapi memastikan hsv baru dari tersegmentasi)
        green_mask = cv2.inRange(hsv, self.lower_green, self.upper_green) # Membuat mask untuk piksel hijau dalam stroberi tersegmentasi
        red_mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1) # Membuat mask untuk rentang merah pertama
        red_mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2) # Membuat mask untuk rentang merah kedua
        red_mask = cv2.bitwise_or(red_mask1, red_mask2) # Menggabungkan mask merah
        
        green_pixels = np.sum(green_mask > 0) # Menghitung piksel hijau
        red_pixels = np.sum(red_mask > 0) # Menghitung piksel merah
        total_pixels = green_pixels + red_pixels # Menghitung total piksel yang berwarna hijau atau merah
        
        color_ratio = { # Menghitung rasio piksel hijau muda dan merah
            "light_green_ratio": green_pixels / total_pixels if total_pixels > 0 else 0, # Rasio piksel hijau muda
            "red_ratio": red_pixels / total_pixels if total_pixels > 0 else 0 # Rasio piksel merah
        }
        
        # Pastikan tidak ada nilai NaN
        color_ratio["light_green_ratio"] = max(0, min(1, color_ratio["light_green_ratio"])) # Memastikan rasio hijau muda antara 0 dan 1
        color_ratio["red_ratio"] = max(0, min(1, color_ratio["red_ratio"])) # Memastikan rasio merah antara 0 dan 1
        
        # Normalisasi jika total melebihi 100%
        total_ratio = color_ratio["light_green_ratio"] + color_ratio["red_ratio"] # Jumlah rasio hijau dan merah
        if total_ratio > 1: # Jika jumlah melebihi 1 (karena potensi tumpang tindih piksel atau pembulatan)
            color_ratio["light_green_ratio"] /= total_ratio # Normalisasi rasio hijau
            color_ratio["red_ratio"] /= total_ratio # Normalisasi rasio merah
        
        color_stats = { # Menyimpan statistik warna yang dihitung
            "hue": float(h_avg) if not np.isnan(h_avg) else 0.0, # Rata-rata Hue, pastikan float dan tangani NaN
            "saturation": float(s_avg) if not np.isnan(s_avg) else 0.0, # Rata-rata Saturation, pastikan float dan tangani NaN
            "value": float(v_avg) if not np.isnan(v_avg) else 0.0, # Rata-rata Value, pastikan float dan tangani NaN
            "light_green_ratio": float(color_ratio["light_green_ratio"]) if not np.isnan(color_ratio["light_green_ratio"]) else 0.0, # Rasio piksel hijau muda, pastikan float dan tangani NaN
            "red_ratio": float(color_ratio["red_ratio"]) if not np.isnan(color_ratio["red_ratio"]) else 0.0 # Rasio piksel merah, pastikan float dan tangani NaN
        }
        
        # Logika kematangan untuk stroberi
        ripeness = "Tidak dapat ditentukan" # Menginisialisasi status kematangan
        confidence = 0 # Menginisialisasi tingkat kepercayaan
        
        if color_ratio["light_green_ratio"] > 0.7: # Jika lebih dari 70% stroberi yang terdeteksi berwarna hijau muda
            ripeness = "Mentah (Hijau Muda)" # Kematangan adalah "Mentah (Hijau Muda)"
            confidence = min(95, color_ratio["light_green_ratio"] * 100) # Kepercayaan sebanding dengan rasio hijau, dibatasi pada 95
        elif color_ratio["light_green_ratio"] > 0.3: # Jika lebih dari 30% berwarna hijau muda (tetapi tidak lebih dari 70%)
            ripeness = "Setengah Matang" # Kematangan adalah "Setengah Matang"
            confidence = 80 # Kepercayaan tetap
        elif s_avg > 200 and v_avg > 200 and color_ratio["red_ratio"] > 0.9: # Jika saturasi dan nilai tinggi, dan lebih dari 90% berwarna merah
            ripeness = "Sangat Matang" # Kematangan adalah "Sangat Matang"
            confidence = min(100, color_ratio["red_ratio"] * 100) # Kepercayaan sebanding dengan rasio merah, dibatasi pada 95
        elif s_avg > 150 and v_avg > 150 and color_ratio["red_ratio"] > 0.7: # Jika saturasi dan nilai cukup tinggi, dan lebih dari 70% berwarna merah
            ripeness = "Matang" # Kematangan adalah "Matang"
            confidence = min(90, color_ratio["red_ratio"] * 100) # Kepercayaan sebanding dengan rasio merah, dibatasi pada 90
        elif color_ratio["red_ratio"] > 0.5: # Jika lebih dari 50% berwarna merah (tetapi kondisi untuk "Matang" atau "Sangat Matang" tidak terpenuhi)
            ripeness = "Setengah Matang" # Kematangan adalah "Setengah Matang"
            confidence = 75 # Kepercayaan tetap
        
        return { # Mengembalikan hasil analisis
            "ripeness": ripeness, # Kematangan yang ditentukan
            "confidence": float(confidence), # Tingkat kepercayaan
            "color_stats": color_stats # Statistik warna yang detail
        }
    
    def analyze_from_base64(self, base64_image): # Metode analisis utama untuk antarmuka web, mengambil string gambar base64
        """Fungsi analisis utama untuk antarmuka web""" # Docstring menjelaskan tujuan metode
        try: # Memulai blok try untuk seluruh proses analisis
            # Konversi base64 ke gambar OpenCV
            image = self.process_base64_image(base64_image) # Memanggil metode untuk mengonversi base64 ke gambar OpenCV
            if image is None: # Jika pemrosesan gambar gagal
                return {"error": "Gagal memproses gambar"} # Mengembalikan pesan kesalahan
            
            # Praproses
            preprocessed = self.preprocess_image(image) # Melakukan praproses gambar
            
            # Segmentasi
            segmented, mask = self.segment_strawberry(preprocessed) # Melakukan segmentasi stroberi dari gambar yang telah dipraproses
            
            # Analisis
            result = self.analyze_ripeness(segmented, mask) # Menganalisis kematangan menggunakan gambar dan mask yang tersegmentasi
            
            return result # Mengembalikan hasil analisis
            
        except Exception as e: # Menangkap pengecualian apa pun yang terjadi selama analisis
            return {"error": f"Error dalam analisis: {str(e)}"} # Mengembalikan pesan kesalahan dengan detail pengecualian