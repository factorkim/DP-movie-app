import sys
import json
import joblib
import os  # <-- 맨 위에 os 모듈이 import 되어 있는지 확인해 주세요!
from sklearn.metrics.pairwise import cosine_similarity

def recommend_fast(user_keyword, top_n=3):
    try:
        # [수정] 현재 recommend.py 파일이 있는 '진짜 폴더 위치'를 절대 경로로 알아냅니다.
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # 폴더 위치와 파일 이름을 안전하게 결합합니다.
        tfidf_path = os.path.join(BASE_DIR, 'tfidf_model.pkl')
        matrix_path = os.path.join(BASE_DIR, 'tfidf_matrix.pkl')
        data_path = os.path.join(BASE_DIR, 'movie_data.pkl')

        # 절대 경로를 이용해 파일 로드
        tfidf = joblib.load(tfidf_path)
        tfidf_matrix = joblib.load(matrix_path)
        df = joblib.load(data_path)
        
    except Exception as e:
        # 에러 메시지에 어떤 경로에서 에러가 났는지 찍어주면 디버깅이 쉬워집니다.
        print(json.dumps([{"title": "에러", "overview": f"모델 로드 실패: {str(e)}"}]))
        return
    # 사용자가 입력한 키워드만 기존 공간의 벡터로 빠르게 변환
    user_vector = tfidf.transform([user_keyword])

    # 코사인 유사도 검사 (이 연산 자체는 0.001초도 안 걸립니다)
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
            "poster_path": row['poster_path'] if row['poster_path'] else "https://via.placeholder.com/150x220?text=No+Poster",
            "release_date": str(row['release_date']) if row['release_date'] else "미정"
        })
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        recommend_fast(keyword)