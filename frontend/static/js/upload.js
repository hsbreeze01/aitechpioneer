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

let uploadArea;
let fileInput;
let uploadBtn;
let uploadProgress;
let progressFill;
let progressText;
let uploadResult;
let resultMessage;
let uploadAnother;
let refreshTasksBtn;
let uploadTasksList;

let selectedFile = null;
let taskRefreshInterval = null;

function handleFileSelect(file) {
    selectedFile = file;
    
    const validTypes = ['application/pdf', 'text/plain', 'text/markdown', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const validExtensions = ['.pdf', '.txt', '.md', '.docx'];
    
    const isValidType = validTypes.includes(file.type) || validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (!isValidType) {
        alert('不支持的文件类型。请上传 PDF、TXT、Markdown 或 DOCX 文件。');
        selectedFile = null;
        return;
    }
    
    document.querySelector('.upload-text').textContent = file.name;
    document.querySelector('.upload-hint').textContent = `文件大小: ${formatFileSize(file.size)}`;
    
    const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
    const documentTitleInput = document.getElementById('documentTitle');
    if (documentTitleInput && !documentTitleInput.value) {
        documentTitleInput.value = fileNameWithoutExt;
    }
}

function getFileType(filename) {
    const ext = filename.toLowerCase().split('.').pop();
    const typeMap = {
        'pdf': 'pdf',
        'txt': 'txt',
        'md': 'md',
        'docx': 'docx'
    };
    return typeMap[ext] || 'txt';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function loadUploadTasks() {
    console.log('loadUploadTasks called');
    try {
        const response = await fetch(`${API_BASE_URL}/upload-tasks`);
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error('获取任务列表失败');
        }
        
        const data = await response.json();
        console.log('Tasks data:', data);
        renderUploadTasks(data.tasks);
        
    } catch (error) {
        console.error('获取任务列表失败:', error);
        uploadTasksList.innerHTML = `
            <div class="empty-tasks">
                <div class="empty-icon">⚠️</div>
                <p class="empty-text">获取任务列表失败</p>
            </div>
        `;
    }
}

function renderUploadTasks(tasks) {
    console.log('renderUploadTasks called with tasks:', tasks);
    if (!tasks || tasks.length === 0) {
        uploadTasksList.innerHTML = `
            <div class="empty-tasks">
                <div class="empty-icon">📋</div>
                <p class="empty-text">暂无上传任务</p>
            </div>
        `;
        return;
    }
    
    uploadTasksList.innerHTML = tasks.map(task => {
        console.log('Rendering task:', task);
        return `
        <div class="task-card">
            <div class="task-info">
                <div class="task-header">
                    <span class="task-name">${task.file_name}</span>
                    <span class="task-status ${task.status}">${getStatusText(task.status)}</span>
                </div>
                <div class="task-meta">
                    <span>创建时间: ${formatTime(task.created_at)}</span>
                    ${task.completed_at ? `<span>完成时间: ${formatTime(task.completed_at)}</span>` : ''}
                </div>
                ${task.status === 'processing' || task.status === 'uploading' ? `
                    <div class="task-progress">
                        <div class="task-progress-bar">
                            <div class="task-progress-fill" style="width: ${task.progress || 0}%"></div>
                        </div>
                        <span class="task-progress-text">${task.progress || 0}%</span>
                    </div>
                ` : ''}
                ${task.error_message ? `
                    <div class="task-error">${task.error_message}</div>
                ` : ''}
            </div>
            <div class="task-actions">
                ${task.status === 'completed' ? `
                    <a href="/document-detail.html?id=${task.document_id}" class="btn btn-secondary btn-small">查看详情</a>
                ` : ''}
                ${task.status === 'failed' ? `
                    <button class="btn btn-secondary btn-small" onclick="retryTask('${task.task_id}')">重试</button>
                    <button class="btn btn-danger btn-small" onclick="deleteTask('${task.task_id}')">删除</button>
                ` : ''}
            </div>
        </div>
    `}).join('');
}

function getStatusText(status) {
    const statusMap = {
        'pending': '等待中',
        'uploading': '上传中',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
    };
    return statusMap[status] || status;
}

function formatTime(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function retryTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/upload-tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('重试失败');
        }
        
        loadUploadTasks();
    } catch (error) {
        console.error('重试失败:', error);
        alert('重试失败: ' + error.message);
    }
}

async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload-tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('删除失败');
        }
        
        loadUploadTasks();
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    uploadArea = document.getElementById('uploadArea');
    fileInput = document.getElementById('fileInput');
    uploadBtn = document.getElementById('uploadBtn');
    uploadProgress = document.getElementById('uploadProgress');
    progressFill = document.getElementById('progressFill');
    progressText = document.getElementById('progressText');
    uploadResult = document.getElementById('uploadResult');
    resultMessage = document.getElementById('resultMessage');
    uploadAnother = document.getElementById('uploadAnother');
    refreshTasksBtn = document.getElementById('refreshTasksBtn');
    uploadTasksList = document.getElementById('uploadTasksList');
    
    console.log('DOM elements loaded:', {
        uploadArea: !!uploadArea,
        fileInput: !!fileInput,
        uploadBtn: !!uploadBtn,
        uploadTasksList: !!uploadTasksList
    });
    
    uploadArea.addEventListener('click', (e) => {
        console.log('Upload area clicked', e.target);
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    uploadArea.addEventListener('dragover', (e) => {
        console.log('Drag over event');
        e.preventDefault();
        uploadArea.style.borderColor = '#6366f1';
        uploadArea.style.background = '#f8fafc';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        console.log('Drag leave event');
        uploadArea.style.borderColor = '#e2e8f0';
        uploadArea.style.background = 'transparent';
    });

    uploadArea.addEventListener('drop', (e) => {
        console.log('Drop event', e.dataTransfer.files);
        e.preventDefault();
        uploadArea.style.borderColor = '#e2e8f0';
        uploadArea.style.background = 'transparent';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        console.log('File input change event', e.target.files);
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    refreshTasksBtn.addEventListener('click', () => {
        loadUploadTasks();
    });

    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert('请先选择文件');
            return;
        }
        
        uploadProgress.classList.remove('hidden');
        uploadResult.classList.add('hidden');
        uploadBtn.disabled = true;
        
        try {
            progressFill.style.width = '20%';
            progressText.textContent = '正在上传文件...';
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('file_type', getFileType(selectedFile.name));
            formData.append('collection_name', 'documents');
            
            const documentTitle = document.getElementById('documentTitle').value.trim();
            if (documentTitle) {
                formData.append('display_name', documentTitle);
            }
            
            const response = await fetch(`${API_BASE_URL}/documents/upload-async`, {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: '上传失败' }));
                throw new Error(error.detail || '上传失败');
            }
            
            const result = await response.json();
            
            progressFill.style.width = '100%';
            progressText.textContent = '任务已创建！';
            
            loadUploadTasks();
            
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
                uploadResult.classList.remove('hidden');
                resultMessage.textContent = `文档 "${selectedFile.name}" 已开始上传，可在下方任务列表查看进度。`;
                uploadBtn.disabled = false;
                
                selectedFile = null;
                fileInput.value = '';
                document.getElementById('documentTitle').value = '';
                document.getElementById('documentDescription').value = '';
                document.querySelector('.upload-text').textContent = '拖拽文件到此处或点击上传';
                document.querySelector('.upload-hint').textContent = '支持 PDF、TXT、Markdown、DOCX 文件';
            }, 500);
            
        } catch (error) {
            console.error('上传失败:', error);
            progressFill.style.width = '0%';
            progressText.textContent = '上传失败: ' + error.message;
            uploadBtn.disabled = false;
            setTimeout(() => {
                uploadProgress.classList.add('hidden');
            }, 3000);
        }
    });

    uploadAnother.addEventListener('click', () => {
        uploadResult.classList.add('hidden');
        progressFill.style.width = '0%';
        
        selectedFile = null;
        fileInput.value = '';
        document.getElementById('documentTitle').value = '';
        document.getElementById('documentDescription').value = '';
        document.querySelector('.upload-text').textContent = '拖拽文件到此处或点击上传';
        document.querySelector('.upload-hint').textContent = '支持 PDF、TXT、Markdown、DOCX 文件';
    });
    
    loadUploadTasks();
    
    taskRefreshInterval = setInterval(() => {
        loadUploadTasks();
    }, 3000);
});

document.addEventListener('beforeunload', () => {
    if (taskRefreshInterval) {
        clearInterval(taskRefreshInterval);
    }
});