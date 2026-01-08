const API_BASE_URL = 'http://localhost:8001/api';

async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: '请求失败' }));
        throw new Error(error.detail || '请求失败');
    }
    
    return response.json();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });
}

async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('请输入问题');
        return;
    }
    
    const useContext = document.getElementById('useContext').checked;
    const topK = parseInt(document.getElementById('topK').value) || 5;
    
    const answerSection = document.getElementById('answerSection');
    const answerContent = document.getElementById('answerContent');
    const answerSources = document.getElementById('answerSources');
    const sourcesList = document.getElementById('sourcesList');
    
    answerSection.classList.remove('hidden');
    answerContent.innerHTML = '<div class="loading">正在思考...</div>';
    answerSources.classList.add('hidden');
    
    try {
        const response = await fetchAPI('/questions/answer', {
            method: 'POST',
            body: JSON.stringify({
                question: question,
                collection_name: 'documents',
                limit: topK,
                score_threshold: 0.7,
            }),
        });
        
        answerContent.innerHTML = `
            <div class="answer-text">${escapeHtml(response.answer)}</div>
        `;
        
        if (response.sources && response.sources.length > 0) {
            answerSources.classList.remove('hidden');
            sourcesList.innerHTML = response.sources.map((source, index) => `
                <div class="source-item">
                    <div class="source-header">
                        <span class="source-index">${index + 1}</span>
                        <span class="source-score">相关度: ${(source.score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="source-content">${escapeHtml(source.content)}</div>
                    <div class="source-meta">
                        <span>文档ID: ${escapeHtml(source.document_id)}</span>
                        <span>Chunk ID: ${escapeHtml(source.chunk_id)}</span>
                    </div>
                </div>
            `).join('');
        }
        
    } catch (error) {
        console.error('提问失败:', error);
        answerContent.innerHTML = `<div class="error">提问失败: ${error.message}</div>`;
    }
}

function clearAnswer() {
    const answerSection = document.getElementById('answerSection');
    const answerContent = document.getElementById('answerContent');
    const answerSources = document.getElementById('answerSources');
    
    answerSection.classList.add('hidden');
    answerContent.innerHTML = '';
    answerSources.classList.add('hidden');
    
    document.getElementById('questionInput').value = '';
}

async function loadHistory() {
    try {
        const response = await fetchAPI('/documents');
        console.log('API Response:', response);
        console.log('Response type:', typeof response);
        console.log('Response.documents:', response.documents);
        console.log('Response.documents type:', typeof response.documents);
        console.log('Response.documents is array:', Array.isArray(response.documents));
        
        const historyList = document.getElementById('historyList');
        
        if (response.documents.length === 0) {
            historyList.innerHTML = '<div class="empty-history">暂无文档</div>';
            return;
        }
        
        historyList.innerHTML = response.documents.map(doc => `
            <div class="history-item">
                <div class="history-title">${escapeHtml(doc.file_name)}</div>
                <div class="history-meta">
                    <span>类型: ${escapeHtml(doc.file_type)}</span>
                    <span>${formatDate(doc.uploaded_at)}</span>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('加载历史记录失败:', error);
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const askBtn = document.getElementById('askBtn');
    const clearAnswerBtn = document.getElementById('clearAnswer');
    const questionInput = document.getElementById('questionInput');
    
    askBtn.addEventListener('click', askQuestion);
    clearAnswerBtn.addEventListener('click', clearAnswer);
    
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            askQuestion();
        }
    });
    
    loadHistory();
});
