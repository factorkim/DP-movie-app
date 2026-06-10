# train.py (고도화 버전)
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Okt  # 한국어 형태소 분석기 추가
import joblib
import re
import os

# 1. 한국어 토크나이저 함수 정의
okt = Okt()

def korean_tokenizer(text):
    # 단어 앞뒤의 의미 없는 문장부호나 특수문자 제거
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    
    # Okt를 이용해 문장에서 '명사(Noun)'만 쏙쏙 골라냅니다.
    # 예: "장난감이 살아 움직인다" -> ["장난감"]
    # 예: "장난감을 좋아하는 아이들" -> ["장난감", "아이들"]
    nouns = okt.nouns(text)
    
    # 한 글자짜리 명사(예: '그', '이', '것', '등')는 단어 특징으로 부적합하므로 
    # 두 글자 이상인 명사만 최종 필터링합니다.
    return [word for word in nouns if len(word) > 1]

def train_and_save_model():
    print("🧠 한국어 형태소 분석 기반 정밀 AI 학습을 시작합니다...")
    
    try:
        df = pd.read_csv('movies.csv', encoding='utf-8')
    except Exception:
        df = pd.read_csv('movies.csv', encoding='utf-8-sig')

    # 줄거리, 장르, 태그 결합
    df['features'] = df['overview'].fillna('') + " " + df['genres'].fillna('') + " " + df['tags'].fillna('')

    # 2. TF-IDF 세팅 시 우리가 만든 한국어 전용 함수(tokenizer)를 지정합니다.
    # ngram_range=(1, 2)를 추가하여 단어 1개짜리뿐만 아니라 연속된 단어 2개 조합(예: '인간 지배', '토이 스토리')도 하나의 특징으로 학습하게 만듭니다.
    tfidf = TfidfVectorizer(
        tokenizer=korean_tokenizer, 
        ngram_range=(1, 2),
        min_df=1 # 92편 소규모 데이터셋이므로 모든 단어 포용
    )
    
    print("-> 데이터를 분석하여 형태소를 분리하고 공간 지도를 그리는 중...")
    tfidf_matrix = tfidf.fit_transform(df['features'])

    # 파일로 저장
    joblib.dump(tfidf, 'tfidf_model.pkl')
    joblib.dump(tfidf_matrix, 'tfidf_matrix.pkl')
    joblib.dump(df, 'movie_data.pkl')

    print("✨ 학습 완료! 형태소 분석 전용 모델 파일 3개가 성공적으로 갱신되었습니다.")

if __name__ == "__main__":
    train_and_save_model()