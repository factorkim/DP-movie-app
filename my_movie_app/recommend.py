# recommend.py
import sys
import json
import joblib
import os
import re
from konlpy.tag import Okt
from sklearn.metrics.pairwise import cosine_similarity

# 시스템 환경 변수를 세팅했으므로 자바 경로 지정 코드(os.environ)는 완전히 삭제합니다.

okt = Okt()
def korean_tokenizer(text):
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    nouns = okt.nouns(text)
    return [word for word in nouns if len(word) > 1]

def recommend_fast(user_keyword, top_n=3):
    try:
        # 스크립트 기준 절대 경로 세팅
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        tfidf = joblib.load(os.path.join(BASE_DIR, 'tfidf_model.pkl'))
        tfidf_matrix = joblib.load(os.path.join(BASE_DIR, 'tfidf_matrix.pkl'))
        df = joblib.load(os.path.join(BASE_DIR, 'movie_data.pkl'))
    except Exception as e:
        print(json.dumps([{"title": "에러", "overview": f"모델 로드 실패: {str(e)}"}]))
        return

    # 사용자 검색어도 형태소 분석 후 벡터 변환
    user_vector = tfidf.transform([user_keyword])

    # 코사인 유사도 연산
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