import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import nltk
from nltk.corpus import stopwords
import stanza

session = requests.session()
ua = UserAgent(verify_ssl=False)
sw = stopwords.words('english')
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma')

#Находит страничку группы
def find_one_band(name):
    try:
        n = 0
        req = session.get(f'https://www.amalgama-lab.com/songs/{name[0].lower()}/', headers={'User-Agent': ua.random})
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')
        artists = soup.find_all('div', {'class': 'list_songs'})
        for i in artists:
            if i.get('title')[17:] == name: #здесь в будущем можно вставить поиск с опечатками
                n = 1
                link = i.get('data-href')
                req2 = session.get('https://www.amalgama-lab.com'+link, headers={'User-Agent': ua.random})
                artist = req2.text
                art_soup = BeautifulSoup(artist, 'html.parser')
                songs = art_soup.find_all('div', {'id': 'songs_nav', 'class': 'col noprint'})
        if n == 1:
            return [songs, link]
        else:
            return 'Такого испольнителя нет :('
    except:
        return 'Что-то пошло не так! Попробуйте другого исполнителя'

#Получает список песен исполнителя в виде супа
def find_lyric(songs, link):
    super_dict = {}
    for song in songs[0].find_all('a'):
        if not song.get('href').startswith('/songs'):
            req_s = session.get('https://www.amalgama-lab.com'+link+song.get('href'), headers={'User-Agent': ua.random})
            s = req_s.text
            song_soup = BeautifulSoup(s, 'html.parser')
            lyric = song_soup.find_all('div', {'class': 'original'})
            txt = ''
            for l in lyric:
                txt += str(l.text + " ")
            super_dict[song.text] = [[txt]]
    return super_dict


def lemmatize(band):
    songs = find_lyric(band[0], band[1])
    nouns = 0
    verbs = 0
    abverbs = 0
    agjectives = 0
    propernouns = 0
    for song, text in songs.items():
        doc = nlp(text[0][0])
        lemmas = ''
        for sent in doc.sentences:
            for word in sent.words:
                if word.upos == 'NOUN': nouns += 1
                elif word.upos == 'VERB': verbs += 1
                elif word.upos == 'ADV': abverbs += 1
                elif word.upos == 'ADJ': agjectives += 1
                elif word.upos == 'PROPN': propernouns += 1
                lmm = str(word.lemma).lower()
                try:
                    if lmm.isalpha() and lmm not in sw:
                        lemmas += lmm + ' '
                except Exception:
                    print(song)
        songs[song] = lemmas
    return [songs, nouns, verbs, abverbs, agjectives, propernouns]

