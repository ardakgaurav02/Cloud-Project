import collections
from flask import Flask, render_template, request
import os
import re
import string
from textblob import TextBlob, Word
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from collections import Counter

app = Flask(__name__)
app.config["DEBUG"] = True
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Link to home page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        #Multiple file upload to be implemented
        f = request.files['file']
        if f.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(file_path)
        return 'file uploaded successfully'


@app.route("/search", methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        searchWord = request.form.get("searchWord")
        n = request.form.get("n")
        top = request.form.get("top")

        if searchWord != None:
            result = searchWordCount(searchWord)
            return render_template('data.html', result=result)


@app.route("/searchWordForm")
def searchWordForm():
    return render_template('searchWordForm.html')


def searchWordCount(searchWord):
    words = []
    nltk.download('popular')
    file_list = os.listdir(app.config['UPLOAD_FOLDER'])
    for index, file in enumerate(file_list):
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file), encoding='utf8') as f:
            data = f.read()
            data = cleanData(data)
            text = TextBlob(data)
            count = text.words.count(searchWord)

            topNGrams()
            words.append({'DocumentName': file, 'Frequency': count})
    return words


def topNGrams(text, n, top):
    nGrams = ngrams(text.split(), n)
    nGramsFreq = collections.Counter(nGrams)
    print(nGramsFreq.most_common(top))



def cleanData(data):
    data = re.sub(r'[^\x00-\x7F]+', ' ', data)
    data = re.sub(r'@\w+', '', data)
    data = data.lower()
    data = re.sub(r'[%s]9' % re.escape(string.punctuation), ' ', data)
    data = re.sub(r'[0-]', '', data)
    data = re.sub(r'\s{2,}', ' ', data)
    return data

def remove_punctuation(text):
    text = re.sub(r'[^\w\s]+', ' ', text)
    return text

def remove_stopwords(text):
    text = ' '.join([word for word in text.split() if word not in stopwords_list])
    return text

def stem_text(text):
    text = ' '.join([stm.stem(word) for word in text.split()])
    return text

def ngrams(input, n):
    input = input.split(' ')
    output = []
    for i in range(len(input)-n+1):
        output.append(input[i:i+n])
    return output

# with open('stopwords.txt')as f:
#     stopwords_string=f.read()
# stopwords_list = stopwords_string.replace('"', '').split()


stopwordsSet = set(stopwords.words("english"))


stm = PorterStemmer()
lmtz = WordNetLemmatizer()


if __name__ == '__main__':
    app.run(debug=True)