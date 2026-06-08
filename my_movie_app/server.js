const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();

// 1. 포트 설정 (Render 환경에서는 process.env.PORT를 자동으로 할당하므로 반드시 이렇게 설정해야 합니다)
const PORT = process.env.PORT || 3000;

// 2. 파이썬 AI 서버 주소 설정
// 로컬 테스트 시에는 'http://127.0.0.1:8000'을 사용하고, 
// Render에 파이썬 서버를 따로 배포했다면 대시보드에서 환경변수(PYTHON_AI_URL)를 설정해 주면 됩니다.
const PYTHON_AI_URL = process.env.PYTHON_AI_URL || 'http://127.0.0.1:8000';

// 3. 미들웨어 세팅
app.use(express.json()); // 프론트엔드에서 보낸 JSON 데이터를 파싱하기 위함

// 4. 정적 파일 서빙
// public 폴더 안에 index.html, style.css, script.js를 넣으면 Express가 자동으로 브라우저에 띄워줍니다.
app.use(express.static(path.join(__dirname, 'public')));

// 5. 영화 키워드 검색 API 엔드포인트
app.post('/api/search', async (req, res) => {
    const { keyword } = req.body;

    // 예외 처리: 키워드가 없는 경우
    if (!keyword) {
        return res.status(400).json({ 
            success: false, 
            message: "키워드가 입력되지 않았습니다." 
        });
    }

    try {
        console.log(`[Express] 파이썬 AI 서버로 키워드 전송 중: "${keyword}"`);

        // 6. 파이썬 AI 서버(FastAPI)로 요청 전달
        // 파이썬 서버의 /recommend 엔드포인트로 JSON 데이터를 주고받습니다.
        const pythonResponse = await axios.post(`${PYTHON_AI_URL}/recommend`, {
            keyword: keyword
        });

        // 파이썬 서버로부터 받은 추천 영화 데이터
        const aiResult = pythonResponse.data;

        // 7. 프론트엔드가 요청한 형태로 정제하여 응답
        // 프론트엔드 script.js가 'result.data'로 접근할 수 있도록 포맷을 맞춥니다.
        res.json({ 
            success: true, 
            data: aiResult.movies 
        });

    } catch (error) {
        console.error("[Express 에러] 파이썬 AI 서버와 통신 실패:", error.message);
        
        // 에러 상황 발생 시 프론트엔드가 멈추지 않도록 안전하게 응답 전달
        res.status(500).json({ 
            success: false, 
            message: "인공지능 추천 시스템을 호출하는 중 오류가 발생했습니다." 
        });
    }
});

// 8. 서버 시작
app.listen(PORT, () => {
    console.log(`==================================================`);
    console.log(`  🎬 픽사 스타일 영화 추천 백엔드 서버 가동 시작!`);
    console.log(`  서버 주소: http://localhost:${PORT}`);
    console.log(`  연동된 AI 주소: ${PYTHON_AI_URL}`);
    console.log(`==================================================`);
});