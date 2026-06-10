# recommend.py
import sys
import json
import joblib
import os
import re
from sklearn.metrics.pairwise import cosine_similarity

# 1. 환경 분석: 현재 서버가 Windows(내 컴퓨터)인지 확인합니다.
IS_WINDOWS = (os.name == 'nt')

if IS_WINDOWS:
    # [내 컴퓨터(로컬)인 경우]: 자바 경로를 잡고 실제 Okt를 가져옵니다.
    os.environ['JAVA_HOME'] = r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot'
    from konlpy.tag import Okt
    okt = Okt()
    
    def korean_tokenizer(text):
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
        nouns = okt.nouns(text)
        return [word for word in nouns if len(word) > 1]
else:
    # [Render 서버(리눅스)인 경우]: 자바(JVM)를 절대 켜지 않도록 Okt를 호출하지 않습니다.
    # 대신 구조가 똑같은 '가짜 토크나이저' 껍데기만 만들어 둡니다.
    # (이 껍데기는 아래 joblib.load를 만나는 순간 로컬의 진짜 뇌로 치환됩니다.)
    def korean_tokenizer(text):
        return text.split()

def recommend_fast(user_keyword, top_n=3):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # 2. 여기서 pkl 파일들을 로드하면, Render 서버에 자바가 없어도
        # 로컬에서 이미 학습 완료된 딕셔너리와 행렬 구조가 이 시스템 안으로 그대로 복사됩니다.
        tfidf = joblib.load(os.path.join(BASE_DIR, 'tfidf_model.pkl'))
        tfidf_matrix = joblib.load(os.path.join(BASE_DIR, 'tfidf_matrix.pkl'))
        df = joblib.load(os.path.join(BASE_DIR, 'movie_data.pkl'))
    except Exception as e:
        print(json.dumps([{"title": "에러", "overview": f"모델 로드 실패: {str(e)}"}]))
        return

    # 사용자 검색어 벡터 변환
    user_vector = tfidf.transform([user_keyword])

    # 유사도 연산
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
    df['similarity'] = similarity_scores
    recommended_df = df.sort_values(by='similarity', ascending=False).head(top_n)

    result = []
    for _, row in recommended_df.iterrows():
        if row['similarity'] == 0:
            continue
        result.append({
            "id": int(row['id']),
            "title": row['title'],
            "overview": row['overview'],
            "genres": str(row['genres']).split(' ') if row['genres'] else [],
            "tags": str(row['tags']).split(' ') if row['tags'] else [],
            "poster_path": row['poster_path'] if row['poster_path'] else "",
            "release_date": str(row['release_date']) if row['release_date'] else "미정"
        })
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        recommend_fast(keyword)