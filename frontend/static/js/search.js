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

async function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const limitSelect = document.getElementById('limitSelect');
    const thresholdSelect = document.getElementById('thresholdSelect');
    const statusSelect = document.getElementById('statusSelect');
    const searchResults = document.getElementById('searchResults');
    
    const query = searchInput.value.trim();
    
    if (!query) {
        alert('请输入检索关键词或问题');
        return;
    }
    
    searchResults.innerHTML = '<div class="loading">检索中...</div>';
    
    try {
        const response = await fetchAPI('/questions/answer', {
            method: 'POST',
            body: JSON.stringify({
                question: query,
                collection_name: 'documents',
                limit: parseInt(limitSelect.value),
                score_threshold: parseFloat(thresholdSelect.value),
            }),
        });
        
        const chunks = response.sources || [];
        
        if (chunks.length === 0) {
            searchResults.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3 class="empty-title">未找到相关内容</h3>
                    <p class="empty-description">尝试使用不同的关键词或调整相似度阈值</p>
                </div>
            `;
            return;
        }
        
        searchResults.innerHTML = chunks.map((source, index) => `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-score">
                        <span class="score-label">相似度:</span>
                        <span class="score-value">${(source.score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="result-actions">
                        <button class="btn btn-secondary btn-small" onclick="copyContent(${index})">复制内容</button>
                    </div>
                </div>
                <div class="result-content">
                    <div class="content-text">${escapeHtml(source.content)}</div>
                </div>
                <div class="result-meta">
                    <div class="meta-item">
                        <span>📄</span>
                        <span>${escapeHtml(source.metadata?.source_file || '未知文档')}</span>
                    </div>
                    <div class="meta-item">
                        <span>📊</span>
                        <span>类型: ${escapeHtml(source.chunk_type || 'unknown')}</span>
                    </div>
                    <div class="meta-item">
                        <span>🏷️</span>
                        <span>状态: ${escapeHtml(source.status || 'unknown')}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('检索失败:', error);
        searchResults.innerHTML = `<div class="error">检索失败: ${error.message}</div>`;
    }
}

function copyContent(index) {
    const resultCards = document.querySelectorAll('.result-card');
    const contentText = resultCards[index].querySelector('.content-text').textContent;
    
    navigator.clipboard.writeText(contentText).then(() => {
        alert('内容已复制到剪贴板');
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制');
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
    
    searchButton.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});