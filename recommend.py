from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Express에서 보낼 요청 데이터 데이터 모델 정의
class KeywordRequest(BaseModel):
    keyword: str

# 1. AI 추천 핵심 함수 (비지도 학습 알고리즘)
def recommend_movies_by_keyword(user_keyword, top_n=3):
    # CSV 데이터 불러오기
    try:
        df = pd.read_csv('movies.csv', encoding='utf-8')
    except Exception:
        # 인코딩 에러 방지용 예외 처리
        df = pd.read_csv('movies.csv', encoding='utf-8-sig')

    # 영화의 특징을 잡을 텍스트 데이터 결합 (줄거리 + 장르 + 태그)
    # 텍스트 간의 유사도를 비교하기 위해 하나의 긴 문자열로 만듭니다.
    df['features'] = df['overview'] + " " + df['genres'] + " " + df['tags']

    # TF-IDF를 이용한 비지도 학습 텍스트 벡터화
    # 수많은 단어 중 중요 키워드의 가중치를 계산하여 컴퓨터가 이해하는 숫자로 변환합니다.
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['features'])

    # 사용자가 입력한 키워드도 동일한 TF-IDF 공간의 벡터로 변환
    user_vector = tfidf.transform([user_keyword])

    # 사용자의 키워드 벡터와 전체 영화 벡터 간의 코사인 유사도 계산
    # 두 벡터 사이의 각도를 이용해 1에 가까울수록 "유사한 맥락"으로 판단합니다.
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    # 유사도가 높은 순서대로 영화 정렬
    df['similarity'] = similarity_scores
    recommended_df = df.sort_values(by='similarity', ascending=False).head(top_n)

    # 결과를 Express 및 프론트엔드가 사용할 수 있는 JSON 친화적 리스트 형태로 가공
    result = []
    for _, row in recommended_df.iterrows():
        # 유사도 점수가 0인(아무 매칭 단어가 없는) 영화는 추천에서 제외할 수도 있습니다.
        if row['similarity'] == 0:
            continue
            
        result.append({
            "id": int(row['id']),
            "title": row['title'],
            "overview": row['overview'],
            "genres": row['genres'].split(' '),  # 배열 형태로 쪼개기
            "tags": row['tags'].split(' '),    # 배열 형태로 쪼개기
            "poster_path": "https://via.placeholder.com/150x220?text=" + row['title'] # 임시 포스터
        })
    
    return result

# 2. Express 서버가 호출할 API 엔드포인트 생성
@app.post("/recommend")
def get_recommendation(request: KeywordRequest):
    user_keyword = request.keyword
    print(f"[Python AI] 전달받은 검색 키워드: {user_keyword}")
    
    # 추천 알고리즘 실행
    movies = recommend_movies_by_keyword(user_keyword, top_n=3)
    
    # 결과를 반환
    return {"movies": movies}

# 로컬에서 직접 실행할 때의 서버 가동 설정
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)