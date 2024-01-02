from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def upload_file():
    return render_template('Renk.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return 'No file part'
        photo = request.files['photo']
        if photo.filename == '':
            return 'No selected file'

        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
        photo.save(photo_path)
        return render_template('Renk.html', photo_path=photo_path)

if __name__ == '__main__':
    app.run(debug=True)