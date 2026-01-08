const API_BASE_URL = 'http://localhost:8001/api';
let selectedChunks = new Set();
let allChunks = [];

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

function updateMergeButtonState() {
    const mergeButton = document.getElementById('mergeButton');
    mergeButton.disabled = selectedChunks.size !== 2;
}

function toggleChunkSelection(chunkId) {
    if (selectedChunks.has(chunkId)) {
        selectedChunks.delete(chunkId);
    } else {
        if (selectedChunks.size >= 2) {
            alert('最多只能选择两个 Chunk 进行合并');
            return;
        }
        selectedChunks.add(chunkId);
    }
    updateMergeButtonState();
    
    const checkbox = document.querySelector(`input[data-chunk-id="${chunkId}"]`);
    if (checkbox) {
        checkbox.checked = selectedChunks.has(chunkId);
    }
}

function getAdjacentChunks(chunkId) {
    const index = allChunks.findIndex(c => c.chunk_id === chunkId);
    if (index === -1) return { prev: null, next: null };
    
    return {
        prev: index > 0 ? allChunks[index - 1] : null,
        next: index < allChunks.length - 1 ? allChunks[index + 1] : null
    };
}

async function mergeWithAdjacent(chunkId, adjacentChunkId) {
    try {
        const preview = await fetchAPI('/chunks/merge/preview', {
            method: 'POST',
            body: JSON.stringify({
                chunk_id_1: chunkId,
                chunk_id_2: adjacentChunkId,
            }),
        });

        const confirmed = confirm(
            `合并预览：\n\n` +
            `Chunk 1 内容:\n${preview.chunk_1_content.substring(0, 100)}...\n\n` +
            `Chunk 2 内容:\n${preview.chunk_2_content.substring(0, 100)}...\n\n` +
            `合并后内容:\n${preview.merged_content.substring(0, 200)}...\n\n` +
            `确定要合并这两个 Chunk 吗？`
        );

        if (!confirmed) {
            return;
        }

        const response = await fetchAPI('/chunks/merge', {
            method: 'POST',
            body: JSON.stringify({
                chunk_id_1: chunkId,
                chunk_id_2: adjacentChunkId,
            }),
        });
        
        alert(`合并成功！\n\n新的 Chunk ID: ${response.chunk_id.substring(0, 8)}...`);
        selectedChunks.clear();
        updateMergeButtonState();
        loadChunks();
    } catch (error) {
        console.error('合并 Chunk 失败:', error);
        alert(`合并失败: ${error.message}`);
    }
}

async function mergeChunks() {
    if (selectedChunks.size !== 2) {
        alert('请选择两个 Chunk 进行合并');
        return;
    }
    
    const chunkIds = Array.from(selectedChunks);
    const chunkId1 = chunkIds[0];
    const chunkId2 = chunkIds[1];
    
    try {
        const preview = await fetchAPI('/chunks/merge/preview', {
            method: 'POST',
            body: JSON.stringify({
                chunk_id_1: chunkId1,
                chunk_id_2: chunkId2,
            }),
        });

        const confirmed = confirm(
            `合并预览：\n\n` +
            `Chunk 1 内容:\n${preview.chunk_1_content.substring(0, 100)}...\n\n` +
            `Chunk 2 内容:\n${preview.chunk_2_content.substring(0, 100)}...\n\n` +
            `合并后内容:\n${preview.merged_content.substring(0, 200)}...\n\n` +
            `确定要合并这两个 Chunk 吗？`
        );

        if (!confirmed) {
            return;
        }

        const response = await fetchAPI('/chunks/merge', {
            method: 'POST',
            body: JSON.stringify({
                chunk_id_1: chunkId1,
                chunk_id_2: chunkId2,
            }),
        });
        
        alert(`合并成功！\n\n新的 Chunk ID: ${response.chunk_id.substring(0, 8)}...`);
        selectedChunks.clear();
        updateMergeButtonState();
        loadChunks();
    } catch (error) {
        console.error('合并 Chunk 失败:', error);
        alert(`合并失败: ${error.message}`);
    }
}

async function loadChunks() {
    const statusFilter = document.getElementById('statusFilter');
    const typeFilter = document.getElementById('typeFilter');
    const chunksList = document.getElementById('chunksList');
    const emptyState = document.getElementById('emptyState');
    
    try {
        const response = await fetchAPI('/chunks');
        allChunks = response.chunks;
        let chunks = [...allChunks];
        
        if (statusFilter.value) {
            chunks = chunks.filter(c => c.status === statusFilter.value);
        }
        
        if (typeFilter.value) {
            chunks = chunks.filter(c => c.chunk_type === typeFilter.value);
        }
        
        if (chunks.length === 0) {
            chunksList.innerHTML = '';
            chunksList.classList.add('hidden');
            emptyState.classList.remove('hidden');
            return;
        }
        
        chunksList.classList.remove('hidden');
        emptyState.classList.add('hidden');
        
        chunksList.innerHTML = chunks.map(chunk => {
            const adjacent = getAdjacentChunks(chunk.chunk_id);
            const prevButton = adjacent.prev && adjacent.prev.document_id === chunk.document_id 
                ? `<button class="btn btn-small btn-merge" onclick="mergeWithAdjacent('${chunk.chunk_id}', '${adjacent.prev.chunk_id}')" title="与前一个Chunk合并">↑ 合并</button>` 
                : '';
            const nextButton = adjacent.next && adjacent.next.document_id === chunk.document_id 
                ? `<button class="btn btn-small btn-merge" onclick="mergeWithAdjacent('${chunk.chunk_id}', '${adjacent.next.chunk_id}')" title="与后一个Chunk合并">↓ 合并</button>` 
                : '';
            const mergeButtons = (prevButton || nextButton) 
                ? `<div class="chunk-merge-actions">${prevButton}${nextButton}</div>` 
                : '';
            
            const undoMergeButton = chunk.merged_from && chunk.merged_from.length > 0
                ? `<button class="btn btn-small btn-undo" onclick="undoMerge('${chunk.chunk_id}')" title="撤销合并">↩ 撤销合并</button>`
                : '';
            
            return `
            <div class="chunk-card" data-chunk-id="${chunk.chunk_id}">
                <div class="chunk-header">
                    <div class="chunk-title">
                        <input type="checkbox" class="chunk-checkbox" data-chunk-id="${chunk.chunk_id}" ${selectedChunks.has(chunk.chunk_id) ? 'checked' : ''} onchange="toggleChunkSelection('${chunk.chunk_id}')">
                        <span class="chunk-id">${escapeHtml(chunk.chunk_id.substring(0, 8))}...</span>
                        <span class="chunk-type ${chunk.chunk_type}">${escapeHtml(chunk.chunk_type)}</span>
                        <span class="chunk-status ${chunk.status}">${escapeHtml(chunk.status)}</span>
                    </div>
                    <div class="chunk-actions">
                        ${mergeButtons}
                        ${undoMergeButton}
                        <select class="status-select" data-chunk-id="${chunk.chunk_id}">
                            <option value="active" ${chunk.status === 'active' ? 'selected' : ''}>活跃</option>
                            <option value="deprecated" ${chunk.status === 'deprecated' ? 'selected' : ''}>已弃用</option>
                            <option value="inactive" ${chunk.status === 'inactive' ? 'selected' : ''}>非活跃</option>
                        </select>
                        <button class="btn btn-danger btn-small" onclick="deleteChunk('${chunk.chunk_id}')">删除</button>
                    </div>
                </div>
                <div class="chunk-content">
                    <div class="content-text">${escapeHtml(chunk.content)}</div>
                </div>
                <div class="chunk-meta">
                    <div class="meta-item">
                        <span>📄</span>
                        <span>文档 ID: ${escapeHtml(chunk.document_id.substring(0, 8))}...</span>
                    </div>
                    <div class="meta-item">
                        <span>📊</span>
                        <span>质量: ${escapeHtml(chunk.quality)}</span>
                    </div>
                    <div class="meta-item">
                        <span>🔢</span>
                        <span>版本: ${chunk.version}</span>
                    </div>
                    <div class="meta-item">
                        <span>📍</span>
                        <span>位置: ${chunk.start_index} - ${chunk.end_index}</span>
                    </div>
                </div>
            </div>
        `;
        }).join('');
        
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', (e) => {
                updateChunkStatus(e.target.dataset.chunkId, e.target.value);
            });
        });
        
    } catch (error) {
        console.error('加载 Chunk 列表失败:', error);
        chunksList.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
    }
}

async function updateChunkStatus(chunkId, newStatus) {
    try {
        await fetchAPI(`/chunks/${chunkId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus }),
        });
        
        alert('Chunk 状态更新成功');
        loadChunks();
    } catch (error) {
        console.error('更新 Chunk 状态失败:', error);
        alert(`更新失败: ${error.message}`);
    }
}

async function deleteChunk(chunkId) {
    if (!confirm('确定要删除这个 Chunk 吗？此操作不可撤销。')) {
        return;
    }
    
    try {
        await fetchAPI(`/chunks/${chunkId}`, {
            method: 'DELETE',
        });
        
        alert('Chunk 删除成功');
        loadChunks();
    } catch (error) {
        console.error('删除 Chunk 失败:', error);
        alert(`删除失败: ${error.message}`);
    }
}

async function undoMerge(chunkId) {
    if (!confirm('确定要撤销这个合并吗？这将恢复原始的两个 Chunk。')) {
        return;
    }
    
    try {
        const response = await fetchAPI('/chunks/merge/undo', {
            method: 'POST',
            body: JSON.stringify({
                merged_chunk_id: chunkId,
            }),
        });
        
        alert(`撤销合并成功！\n\n已恢复 ${response.restored_chunk_ids.length} 个 Chunk`);
        selectedChunks.clear();
        updateMergeButtonState();
        loadChunks();
    } catch (error) {
        console.error('撤销合并失败:', error);
        alert(`撤销失败: ${error.message}`);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = document.getElementById('refreshButton');
    const statusFilter = document.getElementById('statusFilter');
    const typeFilter = document.getElementById('typeFilter');
    const mergeButton = document.getElementById('mergeButton');
    
    refreshButton.addEventListener('click', loadChunks);
    statusFilter.addEventListener('change', loadChunks);
    typeFilter.addEventListener('change', loadChunks);
    mergeButton.addEventListener('click', mergeChunks);
    
    loadChunks();
});