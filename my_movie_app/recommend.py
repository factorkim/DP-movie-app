# recommend.py
import sys
import json
import joblib
from sklearn.metrics.pairwise import cosine_similarity

def recommend_fast(user_keyword, top_n=3):
    try:
        # [핵심] 0부터 학습하는 대신, 이미 완벽하게 학습 완료된 바이너리 파일을 순식간에 로드합니다.
        tfidf = joblib.load('tfidf_model.pkl')
        tfidf_matrix = joblib.load('tfidf_matrix.pkl')
        df = joblib.load('movie_data.pkl')
    except Exception as e:
        # 파일이 없을 때를 대비한 예외 처리
        print(json.dumps([{"title": "에러", "overview": "모델 파일을 찾을 수 없습니다. train.py를 실행하세요."}]))
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