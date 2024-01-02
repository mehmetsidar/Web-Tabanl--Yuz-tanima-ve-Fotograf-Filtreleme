from flask import Flask, render_template, request, jsonify
import face_recognition
import base64
from io import BytesIO
from PIL import Image
import tempfile
import os

app = Flask(__name__)

# Yüz tanıma için kullanılacak klasör
yuzler_klasoru = "Yüzler"

# Flask ana sayfası
@app.route('/')
def index():
    return render_template('basari_siralama.html', klasor_ekle_goster=False)

# Yüz tarama endpoint'i
@app.route('/tara', methods=['POST'])
def tara():
    try:
        # Gelen veriyi JSON formatından çıkar
        data = request.get_json()
        image_data = data['image_data']

        # Base64 verisini PIL Image'e dönüştür
        img_data = base64.b64decode(image_data)
        img = Image.open(BytesIO(img_data))

        # Düşük çözünürlükte resmi aç
        img = img.resize((400, 400))  # İstediğiniz çözünürlüğü ayarlayın

        # Geçici bir dosyaya resmi kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            img.save(temp_image.name)

            # Yüz tanıma işlemleri
            known_encodings = []
            known_names = []

            # Yüzler klasöründeki tüm dosyaları kontrol et
            for isim_klasoru in os.listdir(yuzler_klasoru):
                isim_klasoru_path = os.path.join(yuzler_klasoru, isim_klasoru)

                if os.path.isdir(isim_klasoru_path):
                    for file_name in os.listdir(isim_klasoru_path):
                        file_path = os.path.join(isim_klasoru_path, file_name)

                        # Dosyanın bir resim dosyası olduğundan emin ol
                        if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                            known_image = face_recognition.load_image_file(file_path)
                            known_encoding = face_recognition.face_encodings(known_image)[0]
                            known_encodings.append(known_encoding)
                            known_names.append(isim_klasoru)

            # Gelen resmin kodunu çıkar
            unknown_encoding = face_recognition.face_encodings(face_recognition.load_image_file(temp_image.name))[0]

        # Yüz karşılaştırma
        results = face_recognition.compare_faces(known_encodings, unknown_encoding)

        if any(results):
            taninan_isim = known_names[results.index(True)]
            return jsonify({'message': f'Yüz tanımlandı! Tanınan İsim: {taninan_isim}'})
        else:
            return jsonify({'message': 'Yüz tanımlanamadı!', 'yeni_klasor_goster': True})

    except Exception as e:
        return jsonify({'message': 'Hata: ' + str(e)})

# Yeni endpoint
@app.route('/ekle', methods=['POST'])
def ekle():
    try:
        data = request.get_json()
        yeni_klasor_isim = data.get('yeni_klasor_isim', 'YeniKlasor')
        img_data = data['image_data']

        # Yeni klasörü yarat
        yeni_klasor_path = os.path.join(yuzler_klasoru, yeni_klasor_isim)
        if not os.path.exists(yeni_klasor_path):
            os.makedirs(yeni_klasor_path)

        # Gelen resmi kodunu çıkar
        img_data = base64.b64decode(img_data)
        img = Image.open(BytesIO(img_data))
        img = img.resize((400, 400))  # İstediğiniz çözünürlüğü ayarlayın
        yeni_klasor_resim_path = os.path.join(yeni_klasor_path, f"yuz_{len(os.listdir(yeni_klasor_path)) + 1}.jpg")
        img.save(yeni_klasor_resim_path)

        return jsonify({'message': f'Yeni klasör oluşturuldu ve yüz kaydedildi. Yeni Klasör Adı: {yeni_klasor_isim}'})

    except Exception as e:
        return jsonify({'message': 'Hata: ' + str(e)})

if __name__ == '__main__':
    app.run(debug=True)