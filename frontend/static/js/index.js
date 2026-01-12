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
        
        document.getElementById('total-documents').textContent = totalDocuments;
        document.getElementById('total-chunks').textContent = totalChunks;
        document.getElementById('active-chunks').textContent = activeChunks;
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
});