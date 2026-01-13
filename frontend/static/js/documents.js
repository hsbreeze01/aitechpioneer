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

async function loadDocuments() {
    try {
        const response = await fetchAPI('/documents');
        const documents = response.documents;
        const documentsList = document.getElementById('documentsList');
        const emptyState = document.getElementById('emptyState');
        
        if (documents.length === 0) {
            documentsList.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }
        
        documentsList.classList.remove('hidden');
        emptyState.classList.add('hidden');
        
        documentsList.innerHTML = documents.map(doc => `
            <div class="document-card">
                <div class="document-header">
                    <div class="document-title">${escapeHtml(doc.display_name || doc.file_name)}</div>
                    <div class="document-actions">
                        <a href="/document-detail.html?id=${doc.document_id}" class="btn btn-secondary btn-small">查看详情</a>
                    </div>
                </div>
                <div class="document-meta-vertical">
                    <div class="meta-row">
                        <span class="meta-label">📄 文件名:</span>
                        <span class="meta-value">${escapeHtml(doc.file_name)}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">📁 文件类型:</span>
                        <span class="meta-value">${escapeHtml(doc.file_type)}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">📅 上传时间:</span>
                        <span class="meta-value">${formatDate(doc.uploaded_at)}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">🧩 Chunk数量:</span>
                        <span class="meta-value">${doc.chunk_count}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('加载文档列表失败:', error);
        const documentsList = document.getElementById('documentsList');
        documentsList.innerHTML = `<div class="loading">加载失败: ${error.message}</div>`;
    }
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

document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
});