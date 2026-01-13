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

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const uploadResult = document.getElementById('uploadResult');
const resultMessage = document.getElementById('resultMessage');
const uploadAnother = document.getElementById('uploadAnother');

let selectedFile = null;

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#6366f1';
    uploadArea.style.background = '#f8fafc';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#e2e8f0';
    uploadArea.style.background = 'transparent';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#e2e8f0';
    uploadArea.style.background = 'transparent';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

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
        
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: '上传失败' }));
            throw new Error(error.detail || '上传失败');
        }
        
        const result = await response.json();
        
        progressFill.style.width = '100%';
        progressText.textContent = '上传完成！';
        
        setTimeout(() => {
            uploadProgress.classList.add('hidden');
            uploadResult.classList.remove('hidden');
            resultMessage.textContent = `文档 "${selectedFile.name}" 已成功上传。`;
            uploadBtn.disabled = false;
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
    selectedFile = null;
    fileInput.value = '';
    document.getElementById('documentTitle').value = '';
    document.getElementById('documentDescription').value = '';
    document.querySelector('.upload-text').textContent = '拖拽文件到此处或点击上传';
    document.querySelector('.upload-hint').textContent = '支持 PDF、TXT、Markdown、DOCX 文件';
    uploadResult.classList.add('hidden');
    progressFill.style.width = '0%';
});