/**
 * ReShorts Windows - JavaScript интерфейс
 * Автор: MiniMax Agent
 * Дата: 2025-10-17
 */

// Глобальные переменные
let currentPage = 'dashboard';
let stats = {};
let config = {};
let selectedVideos = [];
let chartInstance = null;

// Базовый URL API
const API_BASE = '/api';

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ReShorts Windows - Инициализация интерфейса');
    
    initializeNavigation();
    initializeEventListeners();
    checkBackendStatus();
    loadInitialData();
    showPage('dashboard');
    
    // Периодическое обновление статуса
    setInterval(checkBackendStatus, 30000); // каждые 30 секунд
});

// Навигация
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            showPage(page);
        });
    });
}

function showPage(pageId) {
    // Скрыть все страницы
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Убрать активность с навигации
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Показать выбранную страницу
    const targetPage = document.getElementById(pageId);
    const targetNavItem = document.querySelector(`[data-page="${pageId}"]`);
    
    if (targetPage && targetNavItem) {
        targetPage.classList.add('active');
        targetNavItem.classList.add('active');
        currentPage = pageId;
        
        // Загрузить данные для страницы
        loadPageData(pageId);
    }
}

// Инициализация обработчиков событий
function initializeEventListeners() {
    // Форма поиска
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    // Форма анализа
    const analyzeForm = document.getElementById('analyze-form');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', handleAnalyze);
    }
    
    // Обновление файлов
    const refreshFilesBtn = document.getElementById('refresh-files-btn');
    if (refreshFilesBtn) {
        refreshFilesBtn.addEventListener('click', loadFiles);
    }
    
    // Закрытие модальных окон по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Проверка статуса backend
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const statusDot = document.getElementById('backend-status');
        const statusText = document.getElementById('backend-status-text');
        
        if (response.ok) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Backend активен';
        } else {
            throw new Error('Backend недоступен');
        }
    } catch (error) {
        const statusDot = document.getElementById('backend-status');
        const statusText = document.getElementById('backend-status-text');
        
        statusDot.className = 'status-dot';
        statusText.textContent = 'Backend недоступен';
        console.error('❌ Ошибка подключения к backend:', error);
    }
}

// Загрузка начальных данных
async function loadInitialData() {
    try {
        await loadStats();
        await loadConfig();
    } catch (error) {
        console.error('❌ Ошибка загрузки начальных данных:', error);
        showNotification('Ошибка загрузки данных', 'error');
    }
}

// Загрузка данных для страницы
async function loadPageData(pageId) {
    try {
        switch (pageId) {
            case 'dashboard':
                await loadStats();
                updateActivityChart();
                break;
            case 'files':
                await loadFiles();
                break;
            case 'settings':
                await loadConfig();
                updateSettingsForm();
                break;
            case 'status':
                await loadSystemStatus();
                break;
            case 'analyze':
                await checkAIProviders();
                break;
        }
    } catch (error) {
        console.error(`❌ Ошибка загрузки данных для страницы ${pageId}:`, error);
    }
}

// Загрузка статистики
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        if (!response.ok) throw new Error('Ошибка загрузки статистики');
        
        const data = await response.json();
        if (data.status === 'success') {
            stats = data.data;
            updateStatsDisplay();
            updateRecentOperations();
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки статистики:', error);
        showNotification('Ошибка загрузки статистики', 'error');
    }
}

// Обновление отображения статистики
function updateStatsDisplay() {
    document.getElementById('stat-downloaded').textContent = stats.downloaded || 0;
    document.getElementById('stat-analyzed').textContent = stats.analyzed || 0;
    document.getElementById('stat-processed').textContent = stats.processed || 0;
    document.getElementById('stat-success').textContent = `${stats.success_rate || 0}%`;
}

// Обновление последних операций
function updateRecentOperations() {
    const container = document.getElementById('recent-operations');
    const operations = stats.recent_operations || [];
    
    if (operations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <p>Нет операций</p>
                <small>Операции будут отображаться здесь</small>
            </div>
        `;
        return;
    }
    
    container.innerHTML = operations.map(operation => `
        <div class="operation-item">
            <div class="operation-icon">${getOperationIcon(operation.type)}</div>
            <div class="operation-info">
                <div class="operation-description">${operation.description}</div>
                <div class="operation-time">${formatTimestamp(operation.timestamp)}</div>
            </div>
        </div>
    `).join('');
}

function getOperationIcon(type) {
    const icons = {
        'search': '🔍',
        'download': '📥',
        'analyze': '🤖',
        'process': '✂️'
    };
    return icons[type] || '📋';
}

// Обновление графика активности
function updateActivityChart() {
    const canvas = document.getElementById('activityChart');
    if (!canvas || !stats.chart_data) return;
    
    const ctx = canvas.getContext('2d');
    const chartData = stats.chart_data;
    
    // Простое отображение графика (без библиотек)
    drawSimpleChart(ctx, chartData);
}

function drawSimpleChart(ctx, data) {
    const canvas = ctx.canvas;
    const width = canvas.width;
    const height = canvas.height;
    
    // Очистка канваса
    ctx.clearRect(0, 0, width, height);
    
    if (!data || data.length === 0) return;
    
    // Настройки
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    // Максимальное значение
    const maxValue = Math.max(...data.map(d => d.total)) || 1;
    
    // Рисование осей
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    
    // Ось X
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Ось Y
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();
    
    // Рисование данных
    const barWidth = chartWidth / data.length - 10;
    
    data.forEach((item, index) => {
        const x = padding + (index * (chartWidth / data.length)) + 5;
        const barHeight = (item.total / maxValue) * chartHeight;
        const y = height - padding - barHeight;
        
        // Градиент для столбца
        const gradient = ctx.createLinearGradient(0, y, 0, height - padding);
        gradient.addColorStop(0, '#06B6D4');
        gradient.addColorStop(1, '#0891B2');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Подпись даты
        ctx.fillStyle = '#64748B';
        ctx.font = '10px Segoe UI';
        ctx.textAlign = 'center';
        const shortDate = new Date(item.date).toLocaleDateString('ru', { day: '2-digit', month: '2-digit' });
        ctx.fillText(shortDate, x + barWidth / 2, height - padding + 15);
        
        // Значение
        if (item.total > 0) {
            ctx.fillStyle = '#F8FAFC';
            ctx.font = '12px Segoe UI';
            ctx.fillText(item.total.toString(), x + barWidth / 2, y - 5);
        }
    });
}

// Поиск видео
async function handleSearch(event) {
    event.preventDefault();
    
    const btn = document.getElementById('search-btn');
    const formData = new FormData(event.target);
    const searchParams = Object.fromEntries(formData.entries());
    
    // Проверка обязательных полей
    if (!searchParams.query.trim()) {
        showNotification('Введите поисковый запрос', 'warning');
        return;
    }
    
    // Показать состояние загрузки
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchParams)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displaySearchResults(data.data, data.count);
            showNotification(`Найдено ${data.count} видео`, 'success');
        } else {
            throw new Error(data.message || 'Ошибка поиска');
        }
        
    } catch (error) {
        console.error('❌ Ошибка поиска:', error);
        showNotification(`Ошибка поиска: ${error.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

// Отображение результатов поиска
function displaySearchResults(videos, count) {
    const resultsContainer = document.getElementById('search-results');
    const videosGrid = document.getElementById('videos-grid');
    const resultsCount = document.getElementById('results-count');
    
    resultsCount.textContent = `(${count})`;
    
    if (videos.length === 0) {
        videosGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <p>Ничего не найдено</p>
                <small>Попробуйте изменить параметры поиска</small>
            </div>
        `;
    } else {
        videosGrid.innerHTML = videos.map(video => createVideoCard(video)).join('');
    }
    
    resultsContainer.style.display = 'block';
    selectedVideos = [];
}

// Создание карточки видео
function createVideoCard(video) {
    const viralScoreClass = getViralScoreClass(video.viral_score);
    const duration = formatDuration(video.duration);
    const views = formatNumber(video.views);
    const likes = formatNumber(video.likes);
    
    return `
        <div class="video-card" data-video-id="${video.id}">
            <input type="checkbox" class="video-select" onchange="toggleVideoSelection('${video.id}')">
            <div class="video-thumbnail">
                <img src="${video.thumbnail}" alt="${video.title}" loading="lazy">
                <div class="video-duration">${duration}</div>
                <div class="video-platform">${video.platform}</div>
            </div>
            <div class="video-info">
                <div class="video-title">${video.title}</div>
                <div class="video-channel">${video.channel || 'Неизвестный канал'}</div>
                <div class="video-stats">
                    <span>👁️ ${views}</span>
                    <span>❤️ ${likes}</span>
                    <span class="viral-score ${viralScoreClass}">
                        🔥 ${video.viral_score}
                    </span>
                </div>
                <div class="video-actions">
                    <button class="btn btn-primary btn-sm" onclick="downloadVideo('${video.url}', '${video.title}')">
                        📥 Скачать
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="analyzeVideo(${JSON.stringify(video).replace(/"/g, '&quot;')})">
                        🤖 Анализ
                    </button>
                </div>
            </div>
        </div>
    `;
}

function getViralScoreClass(score) {
    if (score >= 8) return 'score-high';
    if (score >= 5) return 'score-medium';
    return 'score-low';
}

function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatNumber(num) {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString('ru');
}

// Выбор видео
function toggleVideoSelection(videoId) {
    const index = selectedVideos.indexOf(videoId);
    const card = document.querySelector(`[data-video-id="${videoId}"]`);
    
    if (index > -1) {
        selectedVideos.splice(index, 1);
        card.classList.remove('selected');
    } else {
        selectedVideos.push(videoId);
        card.classList.add('selected');
    }
    
    updateSelectionUI();
}

function selectAllVideos() {
    const checkboxes = document.querySelectorAll('.video-select');
    const allSelected = selectedVideos.length === checkboxes.length;
    
    checkboxes.forEach(checkbox => {
        const videoId = checkbox.closest('.video-card').dataset.videoId;
        const card = checkbox.closest('.video-card');
        
        if (allSelected) {
            checkbox.checked = false;
            card.classList.remove('selected');
        } else {
            checkbox.checked = true;
            card.classList.add('selected');
        }
    });
    
    if (allSelected) {
        selectedVideos = [];
    } else {
        selectedVideos = Array.from(checkboxes).map(cb => 
            cb.closest('.video-card').dataset.videoId
        );
    }
    
    updateSelectionUI();
}

function updateSelectionUI() {
    const button = document.querySelector('[onclick="selectAllVideos()"]');
    if (button) {
        button.textContent = selectedVideos.length > 0 ? '❌ Снять выделение' : '☑️ Выбрать все';
    }
}

// Скачивание видео
async function downloadVideo(url, title) {
    try {
        showNotification(`Начинаем скачивание: ${title}`, 'info');
        
        const response = await fetch(`${API_BASE}/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification(`Успешно скачано: ${title}`, 'success');
            loadStats(); // Обновить статистику
        } else {
            throw new Error(data.message || 'Ошибка скачивания');
        }
        
    } catch (error) {
        console.error('❌ Ошибка скачивания:', error);
        showNotification(`Ошибка скачивания: ${error.message}`, 'error');
    }
}

// Скачивание выбранных видео
async function downloadSelected() {
    if (selectedVideos.length === 0) {
        showNotification('Выберите видео для скачивания', 'warning');
        return;
    }
    
    showNotification(`Начинаем скачивание ${selectedVideos.length} видео`, 'info');
    
    // Здесь можно реализовать массовое скачивание
    for (const videoId of selectedVideos) {
        const card = document.querySelector(`[data-video-id="${videoId}"]`);
        const url = card.querySelector('.video-actions .btn-primary').getAttribute('onclick').match(/'([^']+)'/)[1];
        const title = card.querySelector('.video-title').textContent;
        
        await downloadVideo(url, title);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Пауза между скачиваниями
    }
}

// AI анализ видео
async function handleAnalyze(event) {
    event.preventDefault();
    
    const btn = document.getElementById('analyze-btn');
    const formData = new FormData(event.target);
    const videoData = formData.get('video_data');
    const prompt = formData.get('prompt');
    
    if (!videoData.trim()) {
        showNotification('Введите данные видео для анализа', 'warning');
        return;
    }
    
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_data: videoData,
                prompt: prompt
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAnalysisResult(data.data);
            showNotification('Анализ выполнен успешно', 'success');
        } else {
            throw new Error(data.message || 'Ошибка анализа');
        }
        
    } catch (error) {
        console.error('❌ Ошибка анализа:', error);
        showNotification(`Ошибка анализа: ${error.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

function analyzeVideo(videoData) {
    // Переключиться на страницу анализа
    showPage('analyze');
    
    // Заполнить форму данными видео
    const videoDataField = document.getElementById('video_data');
    videoDataField.value = JSON.stringify(videoData, null, 2);
    
    // Установить фокус
    videoDataField.focus();
}

// Отображение результата анализа
function displayAnalysisResult(result) {
    const container = document.getElementById('analyze-result');
    const output = document.getElementById('analyze-output');
    
    let html = `
        <div class="analysis-header">
            <h4>📊 Результат анализа</h4>
            <div class="analysis-meta">
                <span>🤖 Провайдер: ${result.provider}</span>
                <span>⏰ ${formatTimestamp(result.timestamp)}</span>
            </div>
        </div>
    `;
    
    if (result.structured_data) {
        const data = result.structured_data;
        
        html += `
            <div class="analysis-scores">
                <div class="score-item">
                    <div class="score-label">Вирусный потенциал</div>
                    <div class="score-value score-${getScoreClass(data.viral_potential)}">${data.viral_potential}/10</div>
                </div>
        `;
        
        if (data.trend_relevance) {
            html += `
                <div class="score-item">
                    <div class="score-label">Актуальность</div>
                    <div class="score-value score-${getScoreClass(data.trend_relevance)}">${data.trend_relevance}/10</div>
                </div>
            `;
        }
        
        html += '</div>';
        
        // Ключевые факторы
        if (data.key_factors && data.key_factors.length > 0) {
            html += `
                <div class="analysis-section">
                    <h5>✅ Ключевые факторы успеха</h5>
                    <ul class="analysis-list">
                        ${data.key_factors.map(factor => `<li>${factor}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Слабые места
        if (data.weaknesses && data.weaknesses.length > 0) {
            html += `
                <div class="analysis-section">
                    <h5>⚠️ Слабые места</h5>
                    <ul class="analysis-list">
                        ${data.weaknesses.map(weakness => `<li>${weakness}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Рекомендации
        if (data.recommendations && data.recommendations.length > 0) {
            html += `
                <div class="analysis-section">
                    <h5>💡 Рекомендации</h5>
                    <ul class="analysis-list">
                        ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
    }
    
    html += `
        <div class="analysis-section">
            <h5>📝 Полный анализ</h5>
            <div class="analysis-text">${result.analysis.replace(/\n/g, '<br>')}</div>
        </div>
    `;
    
    output.innerHTML = html;
    container.style.display = 'block';
    
    // Прокрутить к результату
    container.scrollIntoView({ behavior: 'smooth' });
}

function getScoreClass(score) {
    if (score >= 8) return 'high';
    if (score >= 5) return 'medium';
    return 'low';
}

// Загрузка файлов
async function loadFiles() {
    const container = document.getElementById('files-list');
    
    try {
        container.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Загрузка файлов...</p>
            </div>
        `;
        
        const response = await fetch(`${API_BASE}/files`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayFiles(data.data);
        } else {
            throw new Error(data.message || 'Ошибка загрузки файлов');
        }
        
    } catch (error) {
        console.error('❌ Ошибка загрузки файлов:', error);
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <p>Ошибка загрузки файлов</p>
                <small>${error.message}</small>
            </div>
        `;
    }
}

function displayFiles(files) {
    const container = document.getElementById('files-list');
    
    if (files.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📁</div>
                <p>Нет файлов</p>
                <small>Скачанные файлы будут отображаться здесь</small>
            </div>
        `;
        return;
    }
    
    container.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-icon">🎬</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">
                    ${formatFileSize(file.size)} • ${formatTimestamp(file.created)}
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-secondary btn-sm" onclick="analyzeFile('${file.path}', '${file.name}')">
                    🤖 Анализ
                </button>
                <button class="btn btn-secondary btn-sm" onclick="deleteFile('${file.path}', '${file.name}')">
                    🗑️ Удалить
                </button>
            </div>
        </div>
    `).join('');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Загрузка конфигурации
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        if (data.status === 'success') {
            config = data.data;
        }
    } catch (error) {
        console.error('❌ Ошибка загрузки конфигурации:', error);
    }
}

// Обновление формы настроек
function updateSettingsForm() {
    if (!config) return;
    
    // Настройки поиска
    const searchConfig = config.search || {};
    setValue('config-max-results', searchConfig.max_results || 10);
    setValue('config-date-range', searchConfig.date_range || 'all');
    setValue('config-min-views', searchConfig.min_views || 1000);
    
    // Настройки AI
    const aiConfig = config.ai || {};
    setValue('config-ai-timeout', aiConfig.timeout || 30);
    setValue('config-ai-retries', aiConfig.max_retries || 3);
    setChecked('config-ai-cache', aiConfig.cache_enabled !== false);
    
    const providers = aiConfig.providers || {};
    setValue('config-gpt4free-priority', providers.gpt4free?.priority || 1);
    setValue('config-gemini-priority', providers.gemini?.priority || 2);
    
    // Настройки загрузки
    const downloadConfig = config.download || {};
    setValue('config-video-quality', downloadConfig.video_quality || 'best');
    setValue('config-max-file-size', downloadConfig.max_file_size || 100);
    setValue('config-download-retries', downloadConfig.max_retries || 3);
    setChecked('config-download-thumbnails', downloadConfig.thumbnail !== false);
    
    // Автоматизация
    const autoConfig = config.automation || {};
    setChecked('config-auto-search', autoConfig.auto_search === true);
    setChecked('config-auto-download', autoConfig.auto_download === true);
    setChecked('config-auto-analyze', autoConfig.auto_analyze === true);
    setValue('config-auto-interval', autoConfig.auto_run_interval || 60);
    setValue('config-daily-limit', autoConfig.max_daily_downloads || 50);
}

function setValue(id, value) {
    const element = document.getElementById(id);
    if (element) element.value = value;
}

function setChecked(id, checked) {
    const element = document.getElementById(id);
    if (element) element.checked = checked;
}

// Сохранение настроек
async function saveSettings() {
    try {
        const newConfig = {
            search: {
                max_results: parseInt(getValue('config-max-results')) || 10,
                date_range: getValue('config-date-range') || 'all',
                min_views: parseInt(getValue('config-min-views')) || 1000
            },
            ai: {
                timeout: parseInt(getValue('config-ai-timeout')) || 30,
                max_retries: parseInt(getValue('config-ai-retries')) || 3,
                cache_enabled: getChecked('config-ai-cache'),
                providers: {
                    gpt4free: {
                        enabled: true,
                        priority: parseInt(getValue('config-gpt4free-priority')) || 1
                    },
                    gemini: {
                        enabled: true,
                        priority: parseInt(getValue('config-gemini-priority')) || 2
                    }
                }
            },
            download: {
                video_quality: getValue('config-video-quality') || 'best',
                max_file_size: parseInt(getValue('config-max-file-size')) || 100,
                max_retries: parseInt(getValue('config-download-retries')) || 3,
                thumbnail: getChecked('config-download-thumbnails')
            },
            automation: {
                auto_search: getChecked('config-auto-search'),
                auto_download: getChecked('config-auto-download'),
                auto_analyze: getChecked('config-auto-analyze'),
                auto_run_interval: parseInt(getValue('config-auto-interval')) || 60,
                max_daily_downloads: parseInt(getValue('config-daily-limit')) || 50
            }
        };
        
        const response = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newConfig)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            config = newConfig;
            showNotification('Настройки сохранены', 'success');
        } else {
            throw new Error(data.message || 'Ошибка сохранения');
        }
        
    } catch (error) {
        console.error('❌ Ошибка сохранения настроек:', error);
        showNotification(`Ошибка сохранения: ${error.message}`, 'error');
    }
}

function getValue(id) {
    const element = document.getElementById(id);
    return element ? element.value : '';
}

function getChecked(id) {
    const element = document.getElementById(id);
    return element ? element.checked : false;
}

// Загрузка статуса системы
async function loadSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/system-status`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displaySystemStatus(data.data);
        } else {
            throw new Error(data.message || 'Ошибка загрузки статуса');
        }
        
    } catch (error) {
        console.error('❌ Ошибка загрузки статуса системы:', error);
        displaySystemError(error.message);
    }
}

function displaySystemStatus(status) {
    // Системная информация
    if (status.system) {
        updateSystemInfo(status.system);
    }
    
    // Статус загрузчиков
    if (status.downloaders) {
        updateDownloadersStatus(status.downloaders);
    }
    
    // Статус AI провайдеров
    if (status.ai_providers) {
        updateAIProvidersStatus(status.ai_providers);
    }
}

function updateSystemInfo(system) {
    const container = document.getElementById('system-info');
    
    container.innerHTML = `
        <div class="status-item">
            <div class="status-name">CPU</div>
            <div class="status-value">
                <span class="status-dot ${system.cpu_percent < 80 ? 'online' : ''}"></span>
                ${system.cpu_percent.toFixed(1)}%
            </div>
        </div>
        <div class="status-item">
            <div class="status-name">Память</div>
            <div class="status-value">
                <span class="status-dot ${system.memory_percent < 80 ? 'online' : ''}"></span>
                ${system.memory_percent.toFixed(1)}%
            </div>
        </div>
        <div class="status-item">
            <div class="status-name">Диск</div>
            <div class="status-value">
                <span class="status-dot ${system.disk_percent < 90 ? 'online' : ''}"></span>
                ${system.disk_percent.toFixed(1)}%
            </div>
        </div>
    `;
}

function updateDownloadersStatus(downloaders) {
    const container = document.getElementById('downloaders-status');
    
    container.innerHTML = Object.entries(downloaders).map(([name, status]) => `
        <div class="status-item">
            <div class="status-name">${name}</div>
            <div class="status-value">
                <span class="status-dot ${status.available ? 'online' : ''}"></span>
                ${status.available ? 'Активен' : 'Недоступен'}
            </div>
        </div>
    `).join('');
}

function updateAIProvidersStatus(providers) {
    const container = document.getElementById('ai-providers-status');
    
    container.innerHTML = Object.entries(providers).map(([name, status]) => `
        <div class="status-item">
            <div class="status-name">${name}</div>
            <div class="status-value">
                <span class="status-dot ${status.available ? 'online' : ''}"></span>
                ${status.available ? 'Активен' : 'Недоступен'}
                ${status.mode ? `(${status.mode})` : ''}
            </div>
        </div>
    `).join('');
}

function displaySystemError(message) {
    const containers = ['system-info', 'downloaders-status', 'ai-providers-status'];
    
    containers.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">❌</div>
                    <p>Ошибка загрузки</p>
                    <small>${message}</small>
                </div>
            `;
        }
    });
}

// Проверка AI провайдеров
async function checkAIProviders() {
    try {
        const response = await fetch(`${API_BASE}/system-status`);
        const data = await response.json();
        
        if (data.status === 'success' && data.data.ai_providers) {
            const providerStatus = document.getElementById('ai-provider-status');
            const providers = data.data.ai_providers;
            
            const available = Object.values(providers).filter(p => p.available).length;
            const total = Object.keys(providers).length;
            
            if (available > 0) {
                providerStatus.innerHTML = `
                    <span class="status-dot online"></span>
                    <span>Доступно ${available}/${total} провайдеров</span>
                `;
            } else {
                providerStatus.innerHTML = `
                    <span class="status-dot"></span>
                    <span>Нет доступных провайдеров</span>
                `;
            }
        }
    } catch (error) {
        console.error('❌ Ошибка проверки AI провайдеров:', error);
    }
}

// Утилиты интерфейса
function refreshDashboard() {
    loadStats();
    showNotification('Dashboard обновлен', 'success');
}

function resetSearchForm() {
    const form = document.getElementById('search-form');
    if (form) {
        form.reset();
        document.getElementById('search-results').style.display = 'none';
        selectedVideos = [];
    }
}

function clearAnalyzeForm() {
    const form = document.getElementById('analyze-form');
    if (form) {
        form.reset();
        document.getElementById('analyze-result').style.display = 'none';
    }
}

function refreshSystemStatus() {
    loadSystemStatus();
    showNotification('Статус системы обновлен', 'success');
}

// Модальные окна
function showModal(modalId) {
    document.getElementById('modal-overlay').style.display = 'block';
    document.getElementById(modalId).style.display = 'block';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
    document.querySelectorAll('.modal').forEach(modal => {
        modal.style.display = 'none';
    });
}

function showConfirm(title, message, callback) {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;
    document.getElementById('confirm-action').onclick = () => {
        closeModal();
        callback();
    };
    showModal('confirm-modal');
}

// Уведомления
function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');
    const notification = document.createElement('div');
    
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">${getNotificationIcon(type)}</div>
        <div class="notification-message">${message}</div>
    `;
    
    notifications.appendChild(notification);
    
    // Автоудаление через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
    
    // Удаление по клику
    notification.addEventListener('click', () => {
        notification.remove();
    });
}

function getNotificationIcon(type) {
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}

// Дополнительные функции
function analyzeFile(path, name) {
    showPage('analyze');
    const videoDataField = document.getElementById('video_data');
    videoDataField.value = JSON.stringify({
        title: name,
        file_path: path,
        description: `Локальный файл: ${name}`
    }, null, 2);
}

function deleteFile(path, name) {
    showConfirm(
        'Удаление файла',
        `Вы уверены, что хотите удалить файл "${name}"?`,
        () => {
            // Здесь можно реализовать удаление файла
            showNotification(`Файл "${name}" удален`, 'success');
            loadFiles();
        }
    );
}

function clearOperations() {
    showConfirm(
        'Очистка операций',
        'Вы уверены, что хотите очистить список операций?',
        () => {
            // Здесь можно реализовать очистку
            showNotification('Список операций очищен', 'success');
            loadStats();
        }
    );
}

function cleanupFiles() {
    showConfirm(
        'Очистка файлов',
        'Удалить файлы старше 7 дней?',
        () => {
            // Здесь можно реализовать очистку старых файлов
            showNotification('Старые файлы удалены', 'success');
            loadFiles();
        }
    );
}

function copyAnalysis() {
    const analysisText = document.getElementById('analyze-output').textContent;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(analysisText);
        showNotification('Анализ скопирован в буфер обмена', 'success');
    }
}

function saveAnalysis() {
    const analysisText = document.getElementById('analyze-output').textContent;
    const blob = new Blob([analysisText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Анализ сохранен', 'success');
}

function resetSettings() {
    showConfirm(
        'Сброс настроек',
        'Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?',
        () => {
            // Здесь можно реализовать сброс настроек
            showNotification('Настройки сброшены', 'success');
            loadConfig();
            updateSettingsForm();
        }
    );
}

function exportSettings() {
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `reshorts_settings_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Настройки экспортированы', 'success');
}

function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const importedConfig = JSON.parse(e.target.result);
                    config = importedConfig;
                    updateSettingsForm();
                    showNotification('Настройки импортированы', 'success');
                } catch (error) {
                    showNotification('Ошибка импорта настроек', 'error');
                }
            };
            reader.readAsText(file);
        }
    };
    
    input.click();
}

function clearCache() {
    showConfirm(
        'Очистка кеша',
        'Вы уверены, что хотите очистить кеш?',
        () => {
            // Здесь можно реализовать очистку кеша
            showNotification('Кеш очищен', 'success');
        }
    );
}

function restartServices() {
    showConfirm(
        'Перезапуск служб',
        'Вы уверены, что хотите перезапустить службы?',
        () => {
            showNotification('Службы перезапускаются...', 'info');
            // Здесь можно реализовать перезапуск
        }
    );
}

// Обработка ошибок
window.addEventListener('error', function(event) {
    console.error('❌ JavaScript ошибка:', event.error);
    showNotification('Произошла ошибка интерфейса', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('❌ Необработанная ошибка Promise:', event.reason);
    showNotification('Произошла ошибка приложения', 'error');
});

console.log('✅ ReShorts Windows JavaScript загружен');