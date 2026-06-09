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

    result = []
    for _, row in recommended_df.iterrows():
        if row['similarity'] == 0:
            continue
        result.append({
            "id": int(row['id']),
            "title": row['title'],
            "overview": row['overview'],
            "genres": row['genres'].split(' '),
            "tags": row['tags'].split(' '),
            "poster_path": "https://via.placeholder.com/150x220?text=" + row['title']
        })
    
    # [핵심] Express가 읽을 수 있도록 결과를 JSON 문자열로 출력합니다.
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    # Express가 인자로 던져준 검색 키워드를 받습니다.
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        recommend(keyword)