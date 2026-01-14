const API_BASE_URL = 'http://localhost:8000/api';

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
    const scoreThreshold = parseFloat(document.getElementById('scoreThreshold').value) || 0.5;
    
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
                score_threshold: scoreThreshold,
            }),
        });
        
        currentRecordId = response.record_id || null;
        
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
        
        showFeedbackSection();
        
    } catch (error) {
        console.error('提问失败:', error);
        answerContent.innerHTML = `<div class="error">提问失败: ${error.message}</div>`;
    }
}

let currentRecordId = null;

function showFeedbackSection() {
    const feedbackSection = document.getElementById('feedbackSection');
    feedbackSection.classList.remove('hidden');
}

function hideFeedbackSection() {
    const feedbackSection = document.getElementById('feedbackSection');
    feedbackSection.classList.add('hidden');
}

function showFeedbackForm() {
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackButtons = document.querySelector('.feedback-buttons');
    feedbackForm.classList.remove('hidden');
    feedbackButtons.classList.add('hidden');
}

function hideFeedbackForm() {
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackButtons = document.querySelector('.feedback-buttons');
    feedbackForm.classList.add('hidden');
    feedbackButtons.classList.remove('hidden');
}

async function submitFeedback() {
    const rating = document.getElementById('feedbackRating').value;
    const isResolved = document.getElementById('feedbackResolved').value === 'true';
    const comment = document.getElementById('feedbackComment').value;
    
    if (!currentRecordId) {
        alert('没有可提交反馈的记录');
        return;
    }
    
    try {
        const response = await fetchAPI('/qa/feedback', {
            method: 'POST',
            body: JSON.stringify({
                record_id: currentRecordId,
                rating: parseInt(rating),
                is_resolved: isResolved,
                comment: comment || null,
            }),
        });
        
        if (response.success) {
            alert('反馈提交成功！');
            hideFeedbackSection();
        } else {
            alert('反馈提交失败: ' + response.message);
        }
    } catch (error) {
        console.error('提交反馈失败:', error);
        alert('提交反馈失败: ' + error.message);
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

async function loadQaRecords() {
    const filter = document.getElementById('qaRecordsFilter').value;
    const qaRecordsList = document.getElementById('qaRecordsList');
    const qaRecordsStats = document.getElementById('qaRecordsStats');
    
    try {
        let endpoint = '/qa/records';
        if (filter === 'today') {
            endpoint = '/qa/stats/today';
        } else if (filter === 'week') {
            endpoint = '/qa/stats/week';
        }
        
        const response = await fetchAPI(endpoint);
        
        if (filter === 'all') {
            if (response.records.length === 0) {
                qaRecordsList.innerHTML = '<div class="empty-qa-records">暂无QA检索记录</div>';
                qaRecordsStats.innerHTML = '';
                return;
            }
            
            qaRecordsList.innerHTML = response.records.map(record => `
                <div class="qa-record-card">
                    <div class="qa-record-header">
                        <div class="qa-record-question">
                            <span class="question-label">问题:</span>
                            <span class="question-text">${escapeHtml(record.question)}</span>
                        </div>
                        <span class="qa-record-time">${formatDate(record.created_at)}</span>
                    </div>
                    <div class="qa-record-answer">
                        <span class="answer-label">答案:</span>
                        <span class="answer-text">${escapeHtml(record.answer)}</span>
                    </div>
                    <div class="qa-record-chunks">
                        <span class="chunks-label">检索到的Chunk (${record.retrieved_chunks.length}):</span>
                        <div class="chunks-list">
                            ${record.retrieved_chunks.map(chunk => `
                                <div class="qa-record-chunk">
                                    <div class="chunk-header">
                                        <span class="chunk-id">${escapeHtml(chunk.chunk_id.substring(0, 8))}...</span>
                                        <span class="chunk-score">相似度: ${(chunk.score * 100).toFixed(1)}%</span>
                                    </div>
                                    <div class="chunk-content">${escapeHtml(chunk.content.substring(0, 100))}...</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `).join('');
            
            qaRecordsStats.innerHTML = `
                <div class="stats-summary">
                    <span>总记录数: ${response.records.length}</span>
                </div>
            `;
        } else {
            qaRecordsStats.innerHTML = `
                <div class="stats-summary">
                    <span>总记录数: ${response.total_records}</span>
                    <span>总问题数: ${response.total_questions}</span>
                    <span>总Chunk检索数: ${response.total_retrievals}</span>
                </div>
            `;
            
            qaRecordsList.innerHTML = '<div class="empty-qa-records">选择"全部记录"查看详细记录</div>';
        }
        
    } catch (error) {
        console.error('加载QA检索记录失败:', error);
        qaRecordsList.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        qaRecordsStats.innerHTML = '';
    }
}

async function loadQaRecordsByChunk(chunkId) {
    const qaRecordsList = document.getElementById('qaRecordsList');
    const qaRecordsStats = document.getElementById('qaRecordsStats');
    
    try {
        const response = await fetchAPI(`/qa/records/chunk/${chunkId}`);
        
        if (response.records.length === 0) {
            qaRecordsList.innerHTML = '<div class="empty-qa-records">该Chunk未被检索过</div>';
            qaRecordsStats.innerHTML = '';
            return;
        }
        
        qaRecordsList.innerHTML = response.records.map(record => `
            <div class="qa-record-card">
                <div class="qa-record-header">
                    <div class="qa-record-question">
                        <span class="question-label">问题:</span>
                        <span class="question-text">${escapeHtml(record.question)}</span>
                    </div>
                    <span class="qa-record-time">${formatDate(record.created_at)}</span>
                </div>
                <div class="qa-record-answer">
                    <span class="answer-label">答案:</span>
                    <span class="answer-text">${escapeHtml(record.answer)}</span>
                </div>
                <div class="qa-record-chunks">
                    <span class="chunks-label">检索到的Chunk (${record.retrieved_chunks.length}):</span>
                    <div class="chunks-list">
                        ${record.retrieved_chunks.map(chunk => `
                            <div class="qa-record-chunk ${chunk.chunk_id === chunkId ? 'highlighted' : ''}">
                                <div class="chunk-header">
                                    <span class="chunk-id">${escapeHtml(chunk.chunk_id.substring(0, 8))}...</span>
                                    <span class="chunk-score">相似度: ${(chunk.score * 100).toFixed(1)}%</span>
                                </div>
                                <div class="chunk-content">${escapeHtml(chunk.content.substring(0, 100))}...</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
        
        qaRecordsStats.innerHTML = `
            <div class="stats-summary">
                <span>检索次数: ${response.records.length}</span>
            </div>
        `;
        
    } catch (error) {
        console.error('加载Chunk QA检索记录失败:', error);
        qaRecordsList.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        qaRecordsStats.innerHTML = '';
    }
}

async function loadQaRecordsByDocument(documentId) {
    const qaRecordsList = document.getElementById('qaRecordsList');
    const qaRecordsStats = document.getElementById('qaRecordsStats');
    
    try {
        const response = await fetchAPI(`/qa/records/document/${documentId}`);
        
        if (response.records.length === 0) {
            qaRecordsList.innerHTML = '<div class="empty-qa-records">该文档的Chunk未被检索过</div>';
            qaRecordsStats.innerHTML = '';
            return;
        }
        
        qaRecordsList.innerHTML = response.records.map(record => `
            <div class="qa-record-card">
                <div class="qa-record-header">
                    <div class="qa-record-question">
                        <span class="question-label">问题:</span>
                        <span class="question-text">${escapeHtml(record.question)}</span>
                    </div>
                    <span class="qa-record-time">${formatDate(record.created_at)}</span>
                </div>
                <div class="qa-record-answer">
                    <span class="answer-label">答案:</span>
                    <span class="answer-text">${escapeHtml(record.answer)}</span>
                </div>
                <div class="qa-record-chunks">
                    <span class="chunks-label">检索到的Chunk (${record.retrieved_chunks.length}):</span>
                    <div class="chunks-list">
                        ${record.retrieved_chunks.map(chunk => `
                            <div class="qa-record-chunk">
                                <div class="chunk-header">
                                    <span class="chunk-id">${escapeHtml(chunk.chunk_id.substring(0, 8))}...</span>
                                    <span class="chunk-score">相似度: ${(chunk.score * 100).toFixed(1)}%</span>
                                </div>
                                <div class="chunk-content">${escapeHtml(chunk.content.substring(0, 100))}...</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
        
        qaRecordsStats.innerHTML = `
            <div class="stats-summary">
                <span>检索次数: ${response.records.length}</span>
            </div>
        `;
        
    } catch (error) {
        console.error('加载文档QA检索记录失败:', error);
        qaRecordsList.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        qaRecordsStats.innerHTML = '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const askBtn = document.getElementById('askBtn');
    const clearAnswerBtn = document.getElementById('clearAnswer');
    const questionInput = document.getElementById('questionInput');
    const loadQaRecordsBtn = document.getElementById('loadQaRecords');
    const feedbackSatisfiedBtn = document.getElementById('feedbackSatisfied');
    const feedbackUnsatisfiedBtn = document.getElementById('feedbackUnsatisfied');
    const submitFeedbackBtn = document.getElementById('submitFeedback');
    const cancelFeedbackBtn = document.getElementById('cancelFeedback');
    
    askBtn.addEventListener('click', askQuestion);
    clearAnswerBtn.addEventListener('click', clearAnswer);
    loadQaRecordsBtn.addEventListener('click', loadQaRecords);
    
    if (feedbackSatisfiedBtn) {
        feedbackSatisfiedBtn.addEventListener('click', () => {
            document.getElementById('feedbackRating').value = '5';
            document.getElementById('feedbackResolved').value = 'true';
            showFeedbackForm();
        });
    }
    
    if (feedbackUnsatisfiedBtn) {
        feedbackUnsatisfiedBtn.addEventListener('click', () => {
            document.getElementById('feedbackRating').value = '1';
            document.getElementById('feedbackResolved').value = 'false';
            showFeedbackForm();
        });
    }
    
    if (submitFeedbackBtn) {
        submitFeedbackBtn.addEventListener('click', submitFeedback);
    }
    
    if (cancelFeedbackBtn) {
        cancelFeedbackBtn.addEventListener('click', () => {
            hideFeedbackForm();
        });
    }
    
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            askQuestion();
        }
    });
});
