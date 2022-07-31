import MeCab
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import os
import tweepy
from datetime import timedelta
from dotenv import load_dotenv
import re
import demoji

# .envファイルが読み込めない場合記載
load_dotenv()

# API Keyの指定
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_TOKEN_SECRET']


"""
Twitter API認証を行う
"""
def auth_twitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    return api


"""
取得した文字列を形態素解析する
"""
def mecab_analysis(text: str) -> list:
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    tagger.parse('')
    # encode_text = text.encode('utf-8')
    node = tagger.parseToNode(text)
    output = []
    while node:
        if node.surface != '':
            word_type = node.feature.split(',')[0]
            if word_type in ['形容詞', '名詞', '動詞', '副詞']:
                output.append(node.surface)
        node = node.next
        if node is None:
            break

    return output


"""
形態素の最頻出ワードを可視化する
"""
def create_wordcloud(text, imgpath) -> None:
    fpath = "/migmix-1p-20150712/migmix-1p-regular.ttf"
    img_color = np.array(Image.open(imgpath))

    # text = open("constitution.txt", encoding="utf8").read()

    # ストップワードの設定
    stop_words: list = [
        u'てる', u'いる', u'なる', u'れる', u'する', u'ある', u'こと', u'これ', u'さん', u'して',
        u'くれる', u'やる', u'くださる', u'そう', u'せる', u'した', u'思う',
        u'それ', u'ここ', u'ちゃん', u'くん', u'', u'て', u'に', u'を', u'は', u'の',
        u'が', u'と', u'た', u'し', u'で',
        u'ない', u'も', u'な', u'い', u'か', u'ので', u'よう', ''
    ]
    # TODO: 指定ワードを形態素解析してstop_wordsに追加する
    stop_words += ['する', 'せる', 'られる', 'あの', 'する', 'ある', 'とこ',
                   'なる', 'ない', 'ああ', 'れる', 'さん', 'やる', 'この', 'どう', 'そう', '乃木坂', '乃木坂46', '乃木坂４６', '真夏', '全国', '全国ツアー', '2日目', '福岡', 'ライブ', '今日', '2日', '2日間']
    word_cloud = WordCloud(background_color="white", mask=img_color,
                           contour_width=2,
                           contour_color='steelblue',
                           collocations=False,
                           font_path=fpath, width=900, height=500, stopwords=set(stop_words)).generate(text)

    word_cloud.to_file('ikoma_cloud22.png')
    image_array = word_cloud.to_array()
    img = Image.fromarray(image_array)
    img.show()


"""
Tweetを収集する
"""
def tweet_search(keyword: str) -> list:
    api = auth_twitter()
    demoji_list = []
    try:
        for tweet in tweepy.Cursor(api.search_tweets, q=keyword, include_entities=True, tweet_mode='extended', lang='ja').items(10000):
            # JSTに変換
            tweet.created_at += timedelta(hours=9)

            demoji_plaintext = str(demoji.replace(string=tweet.full_text, repl=''))
            demoji_text = re.sub(r'[a-z]', '', demoji_plaintext.replace('\n', ''))

            demoji_list += mecab_analysis(demoji_text)

    except Exception as e:
        print('Error: ', e)

    finally:
        return demoji_list


if __name__ == '__main__':
    wordcloud_list = tweet_search(
        '#真夏の全国ツアー OR #真夏の全国ツアー2022 exclude:retweets')

    create_wordcloud(' '.join(wordcloud_list), './ikoma.png')
