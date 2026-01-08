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

let currentDocumentId = null;
let currentChunks = [];
let editingChunkId = null;

async function loadDocumentDetail() {
    const urlParams = new URLSearchParams(window.location.search);
    currentDocumentId = urlParams.get('id');
    
    if (!currentDocumentId) {
        alert('缺少文档 ID');
        window.location.href = '/documents.html';
        return;
    }
    
    try {
        const document = await fetchAPI(`/documents/${currentDocumentId}`);
        
        document.getElementById('documentTitle').textContent = document.title;
        document.getElementById('fileName').textContent = document.file_name;
        document.getElementById('fileType').textContent = document.file_type;
        document.getElementById('uploadTime').textContent = formatDate(document.uploaded_at);
        
        const chunks = await fetchAPI(`/documents/${currentDocumentId}/chunks`);
        document.getElementById('chunkCount').textContent = chunks.length;
        currentChunks = chunks;
        
        loadChunks();
        
    } catch (error) {
        console.error('加载文档详情失败:', error);
        alert('加载文档详情失败: ' + error.message);
        window.location.href = '/documents.html';
    }
}

function loadChunks(filter = 'all') {
    const chunksList = document.getElementById('chunksList');
    const chunksEmpty = document.getElementById('chunksEmpty');
    
    let filteredChunks = currentChunks;
    
    if (filter !== 'all') {
        filteredChunks = currentChunks.filter(chunk => chunk.status === filter);
    }
    
    if (filteredChunks.length === 0) {
        chunksList.classList.add('hidden');
        chunksEmpty.classList.remove('hidden');
        return;
    }
    
    chunksList.classList.remove('hidden');
    chunksEmpty.classList.add('hidden');
    
    chunksList.innerHTML = filteredChunks.map(chunk => `
        <div class="chunk-card">
            <div class="chunk-header">
                <div class="chunk-content">${escapeHtml(chunk.content.substring(0, 200))}${chunk.content.length > 200 ? '...' : ''}</div>
                <div class="chunk-actions">
                    <button class="btn btn-secondary btn-small" onclick="openEditModal('${chunk.id}')">编辑</button>
                    <button class="btn btn-secondary btn-small" onclick="deleteChunk('${chunk.id}')">删除</button>
                </div>
            </div>
            <div class="chunk-meta">
                <div class="meta-item">
                    <span>📍</span>
                    <span>位置: ${chunk.start_char} - ${chunk.end_char}</span>
                </div>
                <div class="meta-item">
                    <span>📊</span>
                    <span>质量: <span class="quality-badge quality-${chunk.quality}">${getQualityLabel(chunk.quality)}</span></span>
                </div>
                <div class="meta-item">
                    <span>🏷️</span>
                    <span>状态: <span class="status-badge status-${chunk.status}">${getStatusLabel(chunk.status)}</span></span>
                </div>
                <div class="meta-item">
                    <span>🔢</span>
                    <span>版本: ${chunk.version}</span>
                </div>
                ${chunk.deletion_reason ? `
                <div class="meta-item">
                    <span>🗑️</span>
                    <span>删除原因: ${getDeletionReasonLabel(chunk.deletion_reason)}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function getQualityLabel(quality) {
    const labels = {
        'high': '高',
        'repaired': '已修复',
        'suspect': '可疑',
    };
    return labels[quality] || quality;
}

function getStatusLabel(status) {
    const labels = {
        'active': '活跃',
        'deprecated': '已废弃',
        'inactive': '非活跃',
    };
    return labels[status] || status;
}

function getDeletionReasonLabel(reason) {
    const labels = {
        'low_answerability': '可回答性低',
        'redundant': '内容重复',
        'outdated': '内容过时',
        'error': '错误内容',
        'other': '其他',
    };
    return labels[reason] || reason;
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

function openEditModal(chunkId) {
    const chunk = currentChunks.find(c => c.id === chunkId);
    if (!chunk) return;
    
    editingChunkId = chunkId;
    document.getElementById('chunkContent').value = chunk.content;
    document.getElementById('chunkStatus').value = chunk.status;
    
    const deletionReasonGroup = document.getElementById('deletionReasonGroup');
    if (chunk.status === 'inactive') {
        deletionReasonGroup.classList.remove('hidden');
        document.getElementById('deletionReason').value = chunk.deletion_reason || 'other';
    } else {
        deletionReasonGroup.classList.add('hidden');
    }
    
    document.getElementById('chunkModal').classList.remove('hidden');
}

function closeEditModal() {
    editingChunkId = null;
    document.getElementById('chunkModal').classList.add('hidden');
}

async function saveChunk() {
    if (!editingChunkId) return;
    
    const content = document.getElementById('chunkContent').value;
    const status = document.getElementById('chunkStatus').value;
    const deletionReason = status === 'inactive' ? document.getElementById('deletionReason').value : null;
    
    try {
        await fetchAPI(`/chunks/${editingChunkId}`, {
            method: 'PUT',
            body: JSON.stringify({
                content,
                status,
                deletion_reason: deletionReason,
            }),
        });
        
        await loadDocumentDetail();
        closeEditModal();
        
    } catch (error) {
        console.error('保存 chunk 失败:', error);
        alert('保存失败: ' + error.message);
    }
}

async function deleteChunk(chunkId) {
    if (!confirm('确定要删除这个 chunk 吗？')) return;
    
    try {
        await fetchAPI(`/chunks/${chunkId}`, {
            method: 'DELETE',
        });
        
        await loadDocumentDetail();
        
    } catch (error) {
        console.error('删除 chunk 失败:', error);
        alert('删除失败: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadDocumentDetail();
    
    document.getElementById('modalClose').addEventListener('click', closeEditModal);
    document.getElementById('modalCancel').addEventListener('click', closeEditModal);
    document.getElementById('modalSave').addEventListener('click', saveChunk);
    
    document.getElementById('chunkStatus').addEventListener('change', (e) => {
        const deletionReasonGroup = document.getElementById('deletionReasonGroup');
        if (e.target.value === 'inactive') {
            deletionReasonGroup.classList.remove('hidden');
        } else {
            deletionReasonGroup.classList.add('hidden');
        }
    });
    
    document.getElementById('statusFilter').addEventListener('change', (e) => {
        loadChunks(e.target.value);
    });
    
    document.getElementById('chunkModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('chunkModal')) {
            closeEditModal();
        }
    });
});