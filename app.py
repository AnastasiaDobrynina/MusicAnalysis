from flask import Flask, render_template, request
import numpy as np
import wikipedia
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from create_db import db, Bands, Texts
from functions import find_one_band, lemmatize, sw


tfidf = TfidfVectorizer(
            analyzer="word",  # анализировать по словам
            stop_words=sw,  # передаём список стоп-слов для русского из NLTK
            ngram_range=(1, 3),  # от 1 до 3 слов
            min_df=3  # встретились минимум 3 раза
        )
wikipedia.set_lang('ru')


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datum.db'
db.app = app
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def home():
    return render_template('mainpage.html')


@app.route('/search', methods=['GET'])
def anketa():
    return render_template('search.html')

# warning - пишет, что группа не нашлась

@app.route('/res', methods=['GET'])
def question_page():
    name = dict(request.args)['q']
    # Stanza не поместилась на pythonanywhere, поэтому дальнейший код работать не будет, искать серез интернет нельзя
    # на Амальгаме, если исполнитель начинается с the, артикль переносится в конец
    if name.lower().startswith('the '):
        name = name[4:] + ', ' + name[:3]
    # проверка на повторяемость
    lst = [i.band_name.lower() for i in Bands.query.all()] #игнорируем кейс
    if name.lower() not in lst:
        band1 = find_one_band(name)
        if type(band1) == str:
            # попробуем написать кажое слово с большой буквы
            band1 = find_one_band(name.title())
            if type(band1) == str:
                # попробуем написать капсом
                band1 = find_one_band(name.upper())
                if type(band1) == str:
                    #попробуем написать все маленькими
                    band1 = find_one_band(name.lower())
                    if type(band1) == str:
                        #print(band1)
                        return render_template('search.html', warning=band1)

        all_data = lemmatize(band1)
        data = all_data[0]
        nouns = all_data[1]
        verbs = all_data[2]
        adverbs = all_data[3]
        adjectives = all_data[4]
        propernouns = all_data[5]

        band = Bands(
            band_name=name.lower(),
            verbs=verbs,
            nouns=nouns,
            adjectives=adjectives,
            adverbs=adverbs,
            propernouns=propernouns
                )
        db.session.add(band)
        db.session.commit()
        for n, t in data.items():
            texts = Texts(
                text=t,
                band_id=band.id,
                song_name=n
            )
            db.session.add(texts)

        db.session.commit()
        db.session.refresh(band)
        db.session.refresh(texts)

    else:
        # берем из базы
        name = name.lower()
        name_id = db.session.query(Bands).filter(Bands.band_name == name) # фильтруем по названию
        for k in name_id:
            verbs = k.verbs
            nouns = k.nouns
            adjectives = k.adjectives
            adverbs = k.adverbs
            propernouns = k.propernouns
        for i in name_id:
            our_id = i.id
        all_texts = db.session.query(Texts).filter(Texts.band_id == our_id)
        data = {}
        for txt in all_texts:
            data[txt.song_name] = txt.text
    #1. количество уникальных словоформ, общий размер корпуса, самое частое слово
    overall = 0
    unique = set()
    cnt = Counter()
    for text in data.values():
        overall += len(text.split())
        cnt += Counter(text.split())
        for lmm in text.split():
            unique.add(lmm)
    wordcount = len(unique)
    freq_words = cnt.most_common(10)

    try:
        #2.  tf-idf - ключевые слова
        songs_tfidf = tfidf.fit_transform(data.values())
        feature_names = np.array(tfidf.get_feature_names_out())
        sorted_nzs = np.argsort(songs_tfidf.data)[:-(11):-1]
        key_words = feature_names[songs_tfidf.indices[sorted_nzs]]
    except: return render_template('search.html', warning='Что-то пошло не так! Попробуйте другого исполнителя')

    #3. tf-idf похожие песни
    X = np.array(songs_tfidf.todense())
    labels = list(data.keys())
    pca = PCA(n_components=2)
    coords = np.asarray(pca.fit_transform(X))
    ddd = []
    for coord in coords:
        ddd.append({'x': coord[0], 'y':  coord[1]})

    #4. Выведем немного информации из википедии для разнообразия
    try:
        wiki = wikipedia.page(name).content.split('\n')[0]
    except: wiki = 'У вас отличный вкус!'


    return render_template('stats.html',
                           arg=dict(request.args),
                           verbs=verbs,
                           nouns=nouns,
                           adjectives=adjectives,
                           adverbs=adverbs,
                           propernouns=propernouns,
                           wordcount=wordcount,
                           overall=overall,
                           key_words=key_words,
                           freq_words=freq_words,
                           data=ddd,
                           labels=labels,
                           wiki = wiki
                           )

@app.route('/all_stats', methods=['GET'])
def all_stats():
    # собираем словарь: ключ - название группы, значение - все тексты
    data = {}
    all_bands = db.session.query(Bands)
    for band in all_bands:
        songs = ''
        all_texts = db.session.query(Texts).filter(Texts.band_id == band.id)
        for txt in all_texts:
            songs += txt.text + ' '
        data[band.band_name] = songs
    # делаем tf-idf для кажой группы и делаем PCA
    bands_tfidf = tfidf.fit_transform(data.values())
    X = np.array(bands_tfidf.todense())
    labels = list(data.keys())
    pca = PCA(n_components=2)
    coords = np.asarray(pca.fit_transform(X))
    ddd = []
    for coord in coords:
        ddd.append({'x': coord[0], 'y': coord[1]})


    return render_template('all_stats.html', data=ddd, labels=labels)

if __name__ == '__main__':
    app.run(debug=True)
