// EPUB/PDF轉換器前端邏輯

let uploadedFile = null;
let conversionResult = null;

// DOM元素
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileType = document.getElementById('fileType');
const lineHeight = document.getElementById('lineHeight');
const lineHeightValue = document.getElementById('lineHeightValue');
const convertBtn = document.getElementById('convertBtn');
const downloadBtn = document.getElementById('downloadBtn');
const selectFileBtn = document.getElementById('selectFileBtn');

// 步驟區域
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadSystemStatus();
    updateLineHeightDisplay();
});

function setupEventListeners() {
    // 檔案輸入
    fileInput.addEventListener('change', handleFileSelect);

    // 選擇檔案按鈕
    selectFileBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log('Select file button clicked');
        fileInput.click();
    });

    // 拖拽上傳
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // 點擊上傳區域觸發檔案選擇（避免重複觸發）
    uploadArea.addEventListener('click', function(e) {
        // 確保不是點擊按鈕或檔案輸入
        if (!e.target.closest('button') && e.target !== fileInput) {
            // 只有點擊上傳區域本身時才觸發
            if (e.target === uploadArea ||
                e.target.closest('.upload-content') === uploadArea.querySelector('.upload-content')) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Upload area clicked');
                fileInput.click();
            }
        }
    });

    // 行距調整
    lineHeight.addEventListener('input', updateLineHeightDisplay);

    // 轉換按鈕
    convertBtn.addEventListener('click', startConversion);

    // 下載按鈕
    downloadBtn.addEventListener('click', downloadFile);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function uploadFile(file) {
    // 檢查檔案類型
    const allowedTypes = ['application/epub+zip', 'application/pdf'];
    const allowedExtensions = ['.epub', '.pdf'];
    
    const isValidType = allowedTypes.includes(file.type) || 
                       allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (!isValidType) {
        showError('不支援的檔案格式，請選擇 EPUB 或 PDF 檔案');
        return;
    }
    
    // 檢查檔案大小 (100MB)
    if (file.size > 100 * 1024 * 1024) {
        showError('檔案太大，請選擇小於 100MB 的檔案');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // 顯示上傳進度
    showProgress('上傳檔案中...');
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();
        
        if (data.success) {
            uploadedFile = data;
            showFileInfo(data);
            showStep2();
        } else {
            showError(data.error || '檔案上傳失敗');
        }
    })
    .catch(error => {
        hideProgress();
        showError('上傳過程發生錯誤: ' + error.message);
    });
}

function showFileInfo(data) {
    fileName.textContent = data.filename;
    fileSize.textContent = data.file_size;
    fileType.textContent = data.file_type.toUpperCase();
    
    // 根據檔案類型調整選項
    if (data.file_type === 'pdf') {
        // PDF可以轉換為EPUB或Markdown
        document.getElementById('formatEpub').disabled = false;
        document.getElementById('formatMd').disabled = false;
        // 預設選擇EPUB格式
        document.getElementById('formatEpub').checked = true;
    }
    
    fileInfo.style.display = 'block';
}

function showStep2() {
    step2.style.display = 'block';
    step3.style.display = 'block';
    step2.scrollIntoView({ behavior: 'smooth' });
}

function updateLineHeightDisplay() {
    lineHeightValue.textContent = lineHeight.value;
}

function startConversion() {
    if (!uploadedFile) {
        showError('請先上傳檔案');
        return;
    }
    
    const conversionData = {
        filename: uploadedFile.filename,
        line_height: parseFloat(lineHeight.value),
        output_format: document.querySelector('input[name="outputFormat"]:checked').value,
        convert_simplified: document.getElementById('convertSimplified').checked
    };
    
    showProgress('轉換中，請稍候...');
    hideSteps();
    
    fetch('/convert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(conversionData)
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();
        
        if (data.success) {
            conversionResult = data;
            showResult(data);
        } else {
            showError(data.error || '轉換失敗');
        }
    })
    .catch(error => {
        hideProgress();
        showError('轉換過程發生錯誤: ' + error.message);
    });
}

function showResult(data) {
    const resultContent = document.getElementById('resultContent');
    
    let html = '<div class="result-info">';
    
    if (data.book_info) {
        html += `
            <h6><i class="fas fa-book"></i> 書籍資訊</h6>
            <p><strong>標題:</strong> ${data.book_info.title}</p>
            <p><strong>作者:</strong> ${data.book_info.author}</p>
            <p><strong>語言:</strong> ${data.book_info.language}</p>
        `;
    }
    
    if (data.pdf_info) {
        html += `
            <h6><i class="fas fa-file-pdf"></i> PDF資訊</h6>
            <p><strong>標題:</strong> ${data.pdf_info.title}</p>
            <p><strong>作者:</strong> ${data.pdf_info.author}</p>
            <p><strong>頁數:</strong> ${data.pdf_info.page_count}</p>
        `;
    }
    
    html += `<p><strong>輸出檔案:</strong> ${data.output_file}</p>`;
    
    if (data.conversion_stats) {
        const stats = data.conversion_stats;
        html += `
            <div class="conversion-stats">
                <h6><i class="fas fa-language"></i> 簡繁轉換統計</h6>
                <div class="stat-item">
                    <span>檢測到簡體中文:</span>
                    <span class="badge ${stats.simplified_detected ? 'bg-warning' : 'bg-secondary'}">
                        ${stats.simplified_detected ? '是' : '否'}
                    </span>
                </div>
                <div class="stat-item">
                    <span>執行轉換:</span>
                    <span class="badge ${stats.conversion_performed ? 'bg-success' : 'bg-secondary'}">
                        ${stats.conversion_performed ? '是' : '否'}
                    </span>
                </div>
                ${stats.conversion_performed ? `
                <div class="stat-item">
                    <span>轉換字符數:</span>
                    <span class="badge bg-info">${stats.changed_chars} / ${stats.total_chars}</span>
                </div>
                <div class="stat-item">
                    <span>轉換比例:</span>
                    <span class="badge bg-info">${stats.change_rate}%</span>
                </div>
                ` : ''}
            </div>
        `;
    }
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function downloadFile() {
    if (!conversionResult) {
        showError('沒有可下載的檔案');
        return;
    }
    
    const downloadUrl = `/download/${conversionResult.output_dir}/${conversionResult.output_file}`;
    
    // 創建隱藏的下載連結
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = conversionResult.output_file;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function showProgress(message) {
    document.getElementById('progressText').textContent = message;
    progressSection.style.display = 'block';
}

function hideProgress() {
    progressSection.style.display = 'none';
}

function hideSteps() {
    step1.style.display = 'none';
    step2.style.display = 'none';
    step3.style.display = 'none';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

function loadSystemStatus() {
    fetch('/status')
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('systemStatus');
        
        let html = '';
        
        // 簡繁轉換狀態
        const textConverterOk = data.text_converter.includes('已就緒');
        html += `
            <div class="status-item">
                <i class="fas fa-language ${textConverterOk ? 'status-ok' : 'status-warning'}"></i>
                <span>${data.text_converter}</span>
            </div>
        `;
        
        // PDF處理狀態
        html += `
            <div class="status-item">
                <i class="fas fa-file-pdf ${data.pdf_processor_available ? 'status-ok' : 'status-error'}"></i>
                <span>PDF處理: ${data.pdf_processor_available ? '可用' : '不可用'}</span>
            </div>
        `;
        
        // 檔案大小限制
        html += `
            <div class="status-item">
                <i class="fas fa-upload status-ok"></i>
                <span>最大檔案大小: ${data.max_file_size}</span>
            </div>
        `;
        
        statusDiv.innerHTML = html;
    })
    .catch(error => {
        document.getElementById('systemStatus').innerHTML = 
            '<p class="text-danger"><i class="fas fa-exclamation-triangle"></i> 無法載入系統狀態</p>';
    });
}
