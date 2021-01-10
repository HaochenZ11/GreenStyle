from flask import Flask, render_template, request
from werkzeug import secure_filename
import matplotlib.pyplot as plt
from PIL import Image
from query import query
from productrec import give_rec
from classify import classify_image, TransferNet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
filepath = ''

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('home.html')

@app.route('/home/', methods=["GET", "POST"])
def get_file():
    if request.method == 'POST':
        file = request.files['file']
        file.save(secure_filename(file.filename))
        global filepath
        filepath = file.filename
        text = request.form['text']
        processed_text = text.upper()
        return evaluate(processed_text)
    return "Please submit a file."

def evaluate(processed_text):
        storeinfo = query(processed_text)
        rating = storeinfo[0]
        recs = storeinfo[1]
        if rating > 3:
            return render_template('rating.html', processed_text=processed_text, rating=rating)
        else:
            return render_template('classify.html', processed_text=processed_text, rating=rating)

@app.route('/results/', methods=["GET", "POST"])
def results():
    classes = ['bottoms', 'dresses', 'shoes', 'tops']
    global filepath
    pred = classify_image(filepath)
    item = classes[pred]
    recs = give_rec(item, 2)

    store1 = recs[0][0]
    name1 = recs[0][1]
    link1 = recs[0][2]
    img1 = recs[0][3]
    store2 = recs[1][0]
    name2 = recs[1][1]
    link2 = recs[1][2]
    img2 = recs[1][3]

    return render_template('recommend.html', item=item, store1=store1, name1=name1, link1=link1, img1=img1,
                           store2=store2, name2=name2, link2=link2, img2=img2)

if __name__ == '__main__':
    app.run(debug=True)
