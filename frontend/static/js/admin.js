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

async function loadUnsatisfiedRecords() {
    const unsatisfiedRecords = document.getElementById('unsatisfiedRecords');
    const emptyState = document.getElementById('emptyState');
    
    try {
        const response = await fetchAPI('/qa/records/unsatisfied');
        
        if (response.records.length === 0) {
            unsatisfiedRecords.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }
        
        unsatisfiedRecords.classList.remove('hidden');
        emptyState.classList.add('hidden');
        
        unsatisfiedRecords.innerHTML = response.records.map(record => `
            <div class="unsatisfied-record-card">
                <div class="record-header">
                    <div class="record-question">
                        <span class="question-label">问题:</span>
                        <span class="question-text">${escapeHtml(record.question)}</span>
                    </div>
                    <span class="record-time">${formatDate(record.created_at)}</span>
                </div>
                <div class="record-answer">
                    <span class="answer-label">答案:</span>
                    <span class="answer-text">${escapeHtml(record.answer)}</span>
                </div>
                <div class="record-feedback">
                    <span class="feedback-label">用户反馈:</span>
                    ${record.user_feedback ? `
                        <div class="feedback-details">
                            <span class="feedback-rating">评分: ${record.user_feedback.rating || '未评分'}</span>
                            <span class="feedback-resolved ${record.user_feedback.is_resolved === false ? 'unsatisfied' : ''}">
                                ${record.user_feedback.is_resolved === false ? '❌ 未解决' : '✓ 已解决'}
                            </span>
                            ${record.user_feedback.comment ? `
                                <div class="feedback-comment">评论: ${escapeHtml(record.user_feedback.comment)}</div>
                            ` : ''}
                        </div>
                    ` : '<span class="no-feedback">暂无反馈</span>'}
                </div>
                <div class="record-chunks">
                    <span class="chunks-label">检索到的Chunk (${record.retrieved_chunks.length}):</span>
                    <div class="chunks-list">
                        ${record.retrieved_chunks.map((chunk, index) => `
                            <div class="chunk-item">
                                <div class="chunk-header">
                                    <span class="chunk-index">Chunk ${index + 1}</span>
                                    <span class="chunk-id">${escapeHtml(chunk.chunk_id.substring(0, 8))}...</span>
                                    <span class="chunk-score">相似度: ${(chunk.score * 100).toFixed(1)}%</span>
                                </div>
                                <div class="chunk-content">${escapeHtml(chunk.content.substring(0, 150))}...</div>
                                <div class="chunk-actions">
                                    <a href="/chunks.html" class="btn btn-small btn-primary">去 Chunk 管理</a>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('加载不满意的记录失败:', error);
        unsatisfiedRecords.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
        emptyState.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = document.getElementById('refreshButton');
    
    if (refreshButton) {
        refreshButton.addEventListener('click', loadUnsatisfiedRecords);
    }
    
    loadUnsatisfiedRecords();
});
