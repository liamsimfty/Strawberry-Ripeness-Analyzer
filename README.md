![image](https://github.com/user-attachments/assets/70c2d14a-0d30-4331-91d5-cbf965eecb9f)

# Strawberry Ripeness Analyzer

Aplikasi web untuk menganalisis tingkat kematangan stroberi menggunakan computer vision. Aplikasi ini menggunakan Flask sebagai backend dan menyediakan antarmuka web yang intuitif untuk mengunggah dan menganalisis gambar stroberi.

## Fitur

- Analisis tingkat kematangan stroberi secara otomatis
- Antarmuka web yang responsif dan mudah digunakan
- Hasil analisis detail termasuk:
  - Tingkat kematangan (Mentah, Setengah Matang, Matang, Sangat Matang)
  - Tingkat kepercayaan analisis
  - Statistik warna (Hue, Saturation, Value)
  - Rasio warna hijau dan merah
  - Rekomendasi berdasarkan tingkat kematangan

## Persyaratan Sistem

- Python 3.8 atau lebih baru
- pip (Python package manager)
- Web browser modern (Chrome, Firefox, Safari, Edge)

## Instalasi

1. Clone repository ini atau download source code
```bash
git clone <repository-url>
cd strawberry-analyzer
```

2. Buat virtual environment (opsional tapi direkomendasikan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Struktur Project

```
strawberry-analyzer/
├── app.py                          # Flask backend
├── strawberry_ripeness_analyzer.py # Analyzer class
├── static/
│   └── index.html                  # Web UI
├── uploads/                        # Temporary image storage
└── requirements.txt                # Dependencies
```

## Menjalankan Aplikasi

1. Pastikan virtual environment aktif (jika menggunakan)
2. Jalankan server Flask
```bash
python app.py
```
3. Buka browser dan akses `http://localhost:5000`

## Penggunaan

1. Buka aplikasi di browser
2. Klik area upload atau tombol "Klik untuk upload gambar"
3. Pilih gambar stroberi (format: JPG, PNG, maksimal 5MB)
4. Klik tombol "Analisis Kematangan"
5. Tunggu hasil analisis
6. Lihat hasil analisis yang mencakup:
   - Tingkat kematangan
   - Tingkat kepercayaan
   - Statistik warna
   - Rekomendasi

## Dependencies

- Flask==2.3.3
- flask-cors==4.0.0
- opencv-python==4.8.1.78
- numpy==1.24.3
- scikit-learn==1.3.0
- pillow==10.0.1

## Troubleshooting

1. Jika gambar tidak terupload:
   - Pastikan ukuran file tidak melebihi 5MB
   - Pastikan format file adalah JPG atau PNG
   - Periksa koneksi internet

2. Jika analisis gagal:
   - Pastikan gambar stroberi jelas dan terang
   - Pastikan stroberi mendominasi frame gambar
   - Coba dengan gambar yang berbeda

3. Jika server tidak berjalan:
   - Pastikan semua dependencies terinstall
   - Pastikan port 5000 tidak digunakan oleh aplikasi lain
   - Periksa log error di terminal

## Kontribusi

Silakan buat pull request untuk kontribusi. Untuk perubahan besar, buka issue terlebih dahulu untuk mendiskusikan perubahan yang diinginkan.

## Lisensi

[MIT License](LICENSE) 
