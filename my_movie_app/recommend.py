# recommend.py
import sys
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend(user_keyword, top_n=3):
    try:
        df = pd.read_csv('movies.csv', encoding='utf-8')
    except Exception:
        df = pd.read_csv('movies.csv', encoding='utf-8-sig')

    df['features'] = df['overview'] + " " + df['genres'] + " " + df['tags']

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['features'])
    user_vector = tfidf.transform([user_keyword])

    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()
    df['similarity'] = similarity_scores
    recommended_df = df.sort_values(by='similarity', ascending=False).head(top_n)

    # recommend.py 파일 내부의 수정을 가할 부분입니다.

    result = []
    for _, row in recommended_df.iterrows():
        if row['similarity'] == 0:
            continue
        result.append({
            "id": int(row['id']),
            "title": row['title'],
            "overview": row['overview'],
            "genres": str(row['genres']).split(' ') if pd.notna(row['genres']) else [],
            "tags": str(row['tags']).split(' ') if pd.notna(row['tags']) else [],
            # [수정] 가짜 placeholder 대신에 TMDb에서 받아온 실제 이미지 주소와 연도를 매핑합니다.
            "poster_path": row['poster_path'] if pd.notna(row['poster_path']) else "https://via.placeholder.com/150x220?text=No+Poster",
            "release_date": str(row['release_date']) if pd.notna(row['release_date']) else "미정"
        })
    
    print(json.dumps(result, ensure_ascii=False))
    
if __name__ == "__main__":
    # Express가 인자로 던져준 검색 키워드를 받습니다.
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        recommend(keyword)