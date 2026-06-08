// HTML 요소 가져오기
const searchBtn = document.getElementById('search-btn');
const keywordInput = document.getElementById('keyword-input');
const recommendationList = document.getElementById('recommendation-list');

// 검색 버튼 클릭 이벤트 리스너
searchBtn.addEventListener('click', async () => {
    const keyword = keywordInput.value.trim();

    // 1. 유효성 검사
    if (!keyword) {
        alert("원하는 영화의 분위기나 키워드를 입력해 주세요! 🎬");
        return;
    }

    // 2. 로딩 화면 표시 (픽사 감성의 아기자기한 문구)
    recommendationList.innerHTML = `
        <div class="loading-box" style="text-align: center; padding: 40px; color: #1A73E8; font-weight: 500;">
            <p>🎈 AI가 픽사 저장고에서 완벽한 영화를 찾고 있습니다...</p>
        </div>
    `;

    try {
        // 3. 백엔드 API 호출 
        // Render 배포 시 프론트와 백엔드가 같은 앱 내에 있다면 상대 경로를 쓰는 것이 좋습니다.
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keyword: keyword })
        });

        // 응답 상태 확인
        if (!response.ok) {
            throw new Error('서버 응답에 문제가 발생했습니다.');
        }

        const result = await response.json();

        // 4. 결과 화면에 그리기
        if (result.success && result.data.length > 0) {
            renderMovies(result.data);
        } else {
            // 추천 결과가 없을 때
            recommendationList.innerHTML = `
                <div class="no-result" style="text-align: center; padding: 40px; color: #7F8C8D;">
                    <p>앗, 입력하신 키워드와 매칭되는 영화를 찾지 못했어요. 다른 키워드로 검색해 보세요! 🔍</p>
                </div>
            `;
        }

    } catch (error) {
        console.error('Error:', error);
        recommendationList.innerHTML = `
            <div class="error-box" style="text-align: center; padding: 40px; color: #E53935; font-weight: 700;">
                <p>⚠️ 서버와의 통신 중 에러가 발생했습니다. 잠시 후 다시 시도해 주세요.</p>
            </div>
        `;
    }
});

// 엔터키를 눌러도 검색이 되도록 편의 기능 추가
keywordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});

// 백엔드에서 받은 영화 배열 데이터를 기반으로 HTML 카드를 생성하는 함수
function renderMovies(movies) {
    // 기존 리스트 비우기
    recommendationList.innerHTML = '';

    // 영화 데이터 순회하며 노드 추가
    movies.forEach(movie => {
        // 포스터 이미지가 없을 경우를 대비한 플레이스홀더 처리
        const posterUrl = movie.poster_path ? movie.poster_path : 'https://via.placeholder.com/150x220?text=No+Poster';
        
        // 장르 배열을 문자열로 변환 (예: ['SF', '드라마'] -> 'SF, 드라마')
        const genres = Array.isArray(movie.genres) ? movie.genres.join(', ') : movie.genres || '미분류';
        
        // 태그 HTML 동적 생성
        let tagsHtml = '';
        if (movie.tags && movie.tags.length > 0) {
            tagsHtml = movie.tags.map(tag => `<span class="tag">#${tag}</span>`).join('');
        }

        // 이전에 정의한 픽사 스타일의 HTML 구조 생성
        const movieArticle = document.createElement('article');
        movieArticle.className = 'movie-item';
        
        movieArticle.innerHTML = `
            <div class="movie-poster">
                <img src="${posterUrl}" alt="${movie.title} 포스터">
            </div>
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <p class="movie-meta"><span class="genre">${genres}</span> | <span class="release-date">${movie.release_date || '미정'}</span></p>
                <p class="movie-plot">${movie.overview || '줄거리 정보가 없습니다.'}</p>
                <div class="movie-tags">
                    ${tagsHtml}
                </div>
            </div>
        `;

        // 리스트에 추가
        recommendationList.appendChild(movieArticle);
    });
}