# train.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib  # 모델 저장 및 로드 라이브러리

def train_and_save_model():
    print("🧠 TF-IDF 비지도 학습 및 모델 저장을 시작합니다...")
    
    # 1. 데이터 불러오기
    try:
        df = pd.read_csv('movies.csv', encoding='utf-8')
    except Exception:
        df = pd.read_csv('movies.csv', encoding='utf-8-sig')

    # 2. 특징(Feature) 문자열 결합
    df['features'] = df['overview'].fillna('') + " " + df['genres'].fillna('') + " " + df['tags'].fillna('')

    # 3. TF-IDF 모델 학습
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['features'])
    
    # 4. 학습된 결과물들(모델, 행렬, 원본데이터)을 파일로 깔끔하게 저장
    # .pkl (Pickle) 파일 형태로 내 하드디스크에 저장됩니다.
    joblib.dump(tfidf, 'tfidf_model.pkl')
    joblib.dump(tfidf_matrix, 'tfidf_matrix.pkl')
    joblib.dump(df, 'movie_data.pkl') # 데이터프레임 자체도 핏하게 저장해두면 csv보다 읽기 빠릅니다.

    print("✨ 학습 완료! 3개의 모델 파일이 성공적으로 저장되었습니다.")
    print("   - tfidf_model.pkl / tfidf_matrix.pkl / movie_data.pkl")

if __name__ == "__main__":
    train_and_save_model()