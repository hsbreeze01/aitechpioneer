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

async function loadStats() {
    try {
        const response = await fetchAPI('/documents');
        const documents = response.documents;
        
        const totalDocuments = documents.length;
        
        const chunksResponse = await fetchAPI('/chunks');
        const chunks = chunksResponse.chunks;
        
        const totalChunks = chunks.length;
        const activeChunks = chunks.filter(c => c.status === 'active').length;
        
        const totalDocumentsEl = document.getElementById('total-documents');
        const totalChunksEl = document.getElementById('total-chunks');
        const activeChunksEl = document.getElementById('active-chunks');
        
        if (totalDocumentsEl) totalDocumentsEl.textContent = totalDocuments;
        if (totalChunksEl) totalChunksEl.textContent = totalChunks;
        if (activeChunksEl) activeChunksEl.textContent = activeChunks;
    } catch (error) {
        console.error('加载统计数据失败:', error);
        const totalDocumentsEl = document.getElementById('total-documents');
        const totalChunksEl = document.getElementById('total-chunks');
        const activeChunksEl = document.getElementById('active-chunks');
        
        if (totalDocumentsEl) totalDocumentsEl.textContent = '-';
        if (totalChunksEl) totalChunksEl.textContent = '-';
        if (activeChunksEl) activeChunksEl.textContent = '-';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    
    setInterval(loadStats, 30000);
});