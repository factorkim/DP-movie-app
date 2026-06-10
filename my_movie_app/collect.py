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
    # --- 월트 디즈니 애니메이션 스튜디오 (62편) ---
    408,     # 백설공주와 일곱 난쟁이 (1937)
    10895,   # 피노키오 (1940)
    756,     # 환타지아 (1940)
    11360,   # 덤보 (1941)
    3170,    # 밤비 (1942)
    11224,   # 신데렐라 (1950)
    12092,   # 이상한 나라의 앨리스 (1951)
    10693,   # 피터 팬 (1953)
    10340,   # 레이디와 트램프 (1955)
    10882,   # 잠자는 숲속의 공주 (1959)
    12230,   # 101마리의 달마시안 (1961)
    9325,    # 정글 북 (1967)
    10112,   # 아리스토캣 (1970)
    11886,   # 로빈 훗 (1973)
    250480,   # 곰돌이 푸의 모험 (1977)
    11319,   # 생쥐 구조대 (1977)
    10948,   # 토드와 코퍼 (1981)
    10957,   # 타란의 대모험 (1985)
    9994,   # 위대한 명탐정 바실 (1986)
    12233,   # 올리버와 친구들 (1988)
    10144,   # 인어공주 (1989)
    11135,   # 코디와 생쥐 구조대 (1990)
    10020,   # 미녀와 야수 (1991)
    812,     # 알라딘 (1992)
    8587,    # 라이온킹 (1994)
    10530,   # 포카혼타스 (1995)
    10545,   # 노틀담의 꼽추 (1996)
    10674,   # 뮬란 (1998)
    37135,   # 타잔 (1999)
    49948,    # 환타지아 2000 (1999)
    11688,   # 쿠스코? 쿠스코! (2000)
    10567,   # 다이노소어 (2000)
    10865,   # 아틀란티스: 잃어버린 제국 (2001)
    9016,   # 보물성 (2002)
    13700,   # 카우 삼총사 (2004)
    9982,   # 치킨 리틀 (2005)
    1267,   # 로빈슨 가족 (2007)
    13053,   # 볼트 (2008)
    10198,   # 공주와 개구리 (2009)
    38757,   # 라푼젤 (2010)
    51162,   # 곰돌이 푸 (2011)
    82690,   # 주먹왕 랄프 (2012)
    109445,  # 겨울왕국 (2013)
    177572,  # 빅 히어로 (2014)
    269149,  # 주토피아 (2016)
    277834,  # 모아나 (2016)
    404368,  # 주먹왕 랄프 2: 인터넷 속으로 (2018)
    330457,  # 겨울왕국 2 (2019)
    527774,  # 라야와 마지막 드래곤 (2021)
    568124,  # 엔칸토: 마법의 세계 (2021)
    877269,  # 스트레인지 월드 (2022)
    1022796, # 위시 (2023)
    1241982, # 모아나 2 (2024)
    1084242, # 주토피아 2 (2025 개봉 예정)

    # --- 픽사 애니메이션 스튜디오 (30편) ---
    862,     # 토이 스토리 (1995)
    9487,    # 벅스 라이프 (1998)
    863,     # 토이 스토리 2 (1999)
    585,     # 몬스터 주식회사 (2001)
    12,      # 니모를 찾아서 (2003)
    9806,    # 인크레더블 (2004)
    920,     # 카 (2006)
    2062,    # 라따뚜이 (2007)
    10681,   # 월-E (2008)
    14160,   # 업 (2009)
    10193,   # 토이 스토리 3 (2010)
    49013,   # 카 2 (2011)
    62177,   # 메리다와 마법의 숲 (Brave, 2012)
    62211,   # 몬스터 대학교 (2013)
    150540,  # 인사이드 아웃 (2015)
    105864,  # 굿 다이노 (2015)
    127380,  # 도리를 찾아서 (2016)
    260514,  # 카 3 (2017)
    354912,  # 코코 (2017)
    260513,  # 인크레더블 2 (2018)
    301528,  # 토이 스토리 4 (2019)
    508439,  # 온워드: 단 하루의 기적 (2020)
    508442,  # 소울 (2020)
    588943,  # 루카 (2021)
    508947,  # 메이의 새빨간 비밀 (Turning Red, 2022)
    718789,  # 버즈 라이트이어 (2022)
    976573,  # 엘리멘탈 (2023)
    1022789, # 인사이드 아웃 2 (2024)
    1022787, # 엘리오 (2025 개봉 예정)
    1327819  # 호퍼스 (2026 개봉 예정)
]

def fetch_movie_data(movie_id):
    # 영화 상세 정보 가져오기 (한국어 설정)
    detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=ko-KR"
    # 영화 키워드(태그) 가져오기
    keywords_url = f"{BASE_URL}/movie/{movie_id}/keywords?api_key={API_KEY}"
    
    try:
        res_detail = requests.get(detail_url).json()
        res_keywords = requests.get(keywords_url).json()
        
        # 장르 처리 (간혹 장르가 없는 클래식 단편 묶음 영화 대응)
        genres = [g['name'] for g in res_detail.get('genres', [])]
        genres_str = " ".join(genres) if genres else "애니메이션"
        
        # 키워드 처리 (TMDb 버전에 따라 키워드가 'keywords' 또는 'results'에 담겨 옵니다)
        raw_keywords = res_keywords.get('keywords', res_keywords.get('results', []))
        keywords = [k['name'] for k in raw_keywords]
        keywords_str = " ".join(keywords[:7]) # 특징 확보를 위해 7개로 확장

        poster_path = res_detail.get('poster_path')
        full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/150x220?text=No+Poster"

        # 출시일 예외 처리 (미개봉작 주토피아2 같은 경우 개봉일이 빈칸으로 올 수 있음)
        release_date = res_detail.get("release_date", "")
        release_year = release_date[:4] if release_date else "개봉예정"

        movie_info = {
            "id": res_detail.get("id"),
            "title": res_detail.get("title"),
            "overview": res_detail.get("overview", "줄거리 정보 준비 중"), # 빈 줄거리 방지
            "genres": genres_str,
            "tags": keywords_str,
            "poster_path": full_poster_url,
            "release_date": release_year
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