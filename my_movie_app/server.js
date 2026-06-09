// server.js
const express = require('express');
const { spawn } = require('child_process'); // 파이썬을 실행할 도구
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/search', (req, res) => {
    const { keyword } = req.body;

    if (!keyword) {
        return res.status(400).json({ success: false, message: "키워드가 없습니다." });
    }

    console.log(`[Express] 파이썬 스크립트 직접 실행 중... 키워드: "${keyword}"`);

    // 'python3 recommend.py "키워드"' 형태로 프로세스 생성 (Windows 환경 테스트 시 'python'으로 변경 가능)
    // Render 환경(리눅스)에서는 무조건 'python3'로 적어야 안전합니다.
    
    // 현재 실행 중인 server.js와 동일한 폴더 안에 있는 recommend.py를 절대 경로로 지정
    const scriptPath = path.join(__dirname, 'recommend.py');
    const pythonProcess = spawn('python3', [scriptPath, keyword]);

    let resultData = '';

    // 파이썬이 print한 데이터를 모으기
    pythonProcess.stdout.on('data', (data) => {
        resultData += data.toString();
    });

    // 파이썬 실행이 끝났을 때
    pythonProcess.on('close', (code) => {
        try {
            // 수집된 대화(print문)를 JSON 객체로 파싱
            const movies = JSON.parse(resultData);
            res.json({ success: true, data: movies });
        } catch (error) {
            console.error("파이썬 결과 파싱 에러:", error.message);
            res.status(500).json({ success: false, message: "추천 데이터 처리 실패" });
        }
    });

    // 파이썬 내부에서 에러가 났을 때
    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python 에러]: ${data}`);
    });
});

app.listen(PORT, () => {
    console.log(`🚀 일체형 서버 오픈! http://localhost:${PORT}`);
});