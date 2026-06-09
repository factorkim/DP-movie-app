# collect.py
import requests
import pandas as pd
import time

# ⚠️ 본인이 발급받은 TMDb API 키를 여기에 넣으세요
API_KEY = "a3eb097fc9105fa7c961badfdceace87"
BASE_URL = "https://api.themoviedb.org/3"

# [Tip] 원하는 영화의 TMDb ID 찾는 방법: 
# TMDB 사이트에서 영화를 검색했을 때 주소창의 번호입니다. 
# 예: 인터스텔라는 https://www.themoviedb.org/movie/157336 -> ID는 157336
target_movie_ids = [
    157336,  # 인터스텔라
    118340,  # 어바웃 타임
    354912,  # 코코
    301528,  # 토이 스토리 4
    603,     # 매트릭스
    508442,  # 소울
    14160,   # 업 (Up)
    62177,   # 브레이브하트
]

def fetch_movie_data(movie_id):
    # 영화 상세 정보 가져오기 (한국어 설정)
    detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=ko-KR"
    # 영화 키워드(태그) 가져오기
    keywords_url = f"{BASE_URL}/movie/{movie_id}/keywords?api_key={API_KEY}"
    
    try:
        res_detail = requests.get(detail_url).json()
        res_keywords = requests.get(keywords_url).json()
        
        # 장르 정제 (예: ['SF', '드라마'])
        genres = [g['name'] for g in res_detail.get('genres', [])]
        genres_str = " ".join(genres)
        
        # 키워드 정제 (태그로 활용)
        keywords = [k['name'] for k in res_keywords.get('keywords', [])]
        keywords_str = " ".join(keywords[:5]) # 너무 많으면 복잡하니 상위 5개만
        
        # 포스터 이미지 풀 경로 생성
        poster_path = res_detail.get('poster_path')
        full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

        movie_info = {
            "id": res_detail.get("id"),
            "title": res_detail.get("title"),
            "overview": res_detail.get("overview", ""),
            "genres": genres_str,
            "tags": keywords_str,
            "poster_path": full_poster_url,
            "release_date": res_detail.get("release_date", "")[:4] # 연도만 추출
        }
        return movie_info
    except Exception as e:
        print(f"ID {movie_id} 수집 중 에러 발생: {e}")
        return None

if __name__ == "__main__":
    print("🎬 TMDb로부터 영화 데이터 수집을 시작합니다...")
    collected_movies = []
    
    for m_id in target_movie_ids:
        print(f"-> 영화 ID {m_id} 가져오는 중...")
        info = fetch_movie_data(m_id)
        if info and info["overview"]: # 줄거리가 있는 경우만 추가
            collected_movies.append(info)
        time.sleep(0.2) # API 과부하 방지 디레이
        
    # 데이터프레임 변환 후 저장
    df = pd.DataFrame(collected_movies)
    df.to_csv("movies.csv", index=False, encoding="utf-8-sig")
    print("✨ 수집 완료! 'movies.csv' 파일이 성공적으로 갱신되었습니다.")