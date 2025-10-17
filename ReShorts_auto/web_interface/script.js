// ReShorts Auto - Main Application Script
// Full integration with backend API

class ReShortsApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.config = {};
        this.stats = {};
        this.currentVideo = null;
        this.presets = [];
        
        this.init();
    }

    async init() {
        this.setupNavigation();
        this.setupEventListeners();
        await this.loadConfig();
        await this.loadDashboard();
        await this.checkBackendStatus();
    }

    // ===== Navigation =====
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                this.navigateTo(page);
            });
        });
    }

    navigateTo(page) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === page) {
                item.classList.add('active');
            }
        });

        // Update pages
        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
        });
        document.getElementById(page).classList.add('active');

        this.currentPage = page;

        // Load page-specific data
        this.loadPageData(page);
    }

    async loadPageData(page) {
        switch(page) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'files':
                await this.loadFiles();
                break;
            case 'status':
                await this.loadStatus();
                break;
            case 'settings':
                await this.loadSettings();
                break;
        }
    }

    // ===== Event Listeners =====
    setupEventListeners() {
        // Search form
        document.getElementById('search-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.searchVideos();
        });

        // Analyze form
        document.getElementById('analyze-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeVideo();
        });

        // Save config
        document.getElementById('save-config-btn').addEventListener('click', () => {
            this.saveConfig();
        });

        // Reset config
        document.getElementById('reset-config-btn').addEventListener('click', () => {
            if (confirm('Сбросить все настройки к значениям по умолчанию?')) {
                this.resetConfig();
            }
        });

        // Refresh files
        document.getElementById('refresh-files-btn').addEventListener('click', () => {
            this.loadFiles();
        });

        // Refresh status
        document.getElementById('refresh-status-btn').addEventListener('click', () => {
            this.loadStatus();
        });

        // Save preset
        document.getElementById('save-preset-btn').addEventListener('click', () => {
            this.showSavePresetModal();
        });

        // Load preset
        document.getElementById('load-preset-btn').addEventListener('click', () => {
            this.showLoadPresetModal();
        });

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.remove('active');
            });
        });

        // Preset modal buttons
        document.getElementById('confirm-save-preset').addEventListener('click', () => {
            this.savePreset();
        });

        document.getElementById('cancel-save-preset').addEventListener('click', () => {
            document.getElementById('preset-modal').classList.remove('active');
        });

        document.getElementById('cancel-load-preset').addEventListener('click', () => {
            document.getElementById('load-preset-modal').classList.remove('active');
        });

        // Video modal
        document.getElementById('close-video-modal').addEventListener('click', () => {
            document.getElementById('video-modal').classList.remove('active');
        });

        document.getElementById('download-video-btn').addEventListener('click', () => {
            if (this.currentVideo) {
                this.downloadVideo(this.currentVideo);
            }
        });
    }

    // ===== API Methods =====
    
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            if (data && method !== 'GET') {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(endpoint, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            this.showNotification('Ошибка API', error.message, 'error');
            throw error;
        }
    }

    // ===== Dashboard =====
    
    async loadDashboard() {
        try {
            const data = await this.apiCall('/api/stats/dashboard');
            
            // Update stats
            document.getElementById('stat-downloaded').textContent = data.stats.total_downloaded;
            document.getElementById('stat-analyzed').textContent = data.stats.total_analyzed;
            document.getElementById('stat-processed').textContent = data.stats.total_processed;
            document.getElementById('stat-success').textContent = data.stats.success_rate + '%';

            // Update recent operations
            this.renderRecentOperations(data.recent_operations);

            // Render chart
            this.renderActivityChart(data.activity_chart);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    renderRecentOperations(operations) {
        const container = document.getElementById('recent-operations');
        
        if (!operations || operations.length === 0) {
            container.innerHTML = '<p class="empty-state">Нет операций</p>';
            return;
        }

        container.innerHTML = operations.map(op => `
            <div class="operation-item">
                <div class="operation-icon ${op.success ? 'success' : 'error'}">
                    ${op.success ? '✅' : '❌'}
                </div>
                <div class="operation-details">
                    <div class="operation-type">${this.getOperationTypeLabel(op.type)}</div>
                    <div class="operation-time">${this.formatDate(op.timestamp)}</div>
                </div>
            </div>
        `).join('');
    }

    renderActivityChart(data) {
        const canvas = document.getElementById('activityChart');
        const ctx = canvas.getContext('2d');
        
        // Simple bar chart implementation
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;
        
        const barWidth = canvas.width / data.length - 10;
        const maxValue = Math.max(...data.map(d => d.total), 1);
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        data.forEach((item, index) => {
            const barHeight = (item.total / maxValue) * (canvas.height - 40);
            const x = index * (barWidth + 10) + 10;
            const y = canvas.height - barHeight - 20;
            
            // Draw bar
            ctx.fillStyle = '#3b82f6';
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw label
            ctx.fillStyle = '#a0a0a0';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(item.date.substring(5), x + barWidth / 2, canvas.height - 5);
            
            // Draw value
            ctx.fillStyle = '#e0e0e0';
            ctx.fillText(item.total, x + barWidth / 2, y - 5);
        });
    }

    // ===== Search =====
    
    async searchVideos() {
        const btn = document.getElementById('search-btn');
        btn.classList.add('loading');
        btn.disabled = true;

        try {
            const formData = new FormData(document.getElementById('search-form'));
            const filters = {};
            
            for (let [key, value] of formData.entries()) {
                if (key === 'exclude_keywords') {
                    filters[key] = value.split(',').map(k => k.trim()).filter(k => k);
                } else if (['min_views', 'max_views', 'min_likes', 'duration_min', 'duration_max'].includes(key)) {
                    filters[key] = parseInt(value) || 0;
                } else if (key === 'min_engagement') {
                    filters[key] = parseFloat(value) || 0;
                } else {
                    filters[key] = value;
                }
            }

            const data = await this.apiCall('/api/search/preview', 'POST', filters);
            
            this.renderSearchResults(data.videos, data.total);
            this.showNotification('Поиск завершен', `Найдено ${data.total} видео`, 'success');
        } catch (error) {
            this.showNotification('Ошибка поиска', error.message, 'error');
        } finally {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    }

    renderSearchResults(videos, total) {
        const resultsCard = document.getElementById('search-results');
        const videosGrid = document.getElementById('videos-grid');
        const resultsCount = document.getElementById('results-count');
        
        resultsCard.style.display = 'block';
        resultsCount.textContent = `(${total})`;
        
        if (!videos || videos.length === 0) {
            videosGrid.innerHTML = '<p class="empty-state">Видео не найдены</p>';
            return;
        }

        videosGrid.innerHTML = videos.map(video => `
            <div class="video-card" data-video-id="${video.id}">
                <img src="${video.thumbnail}" alt="${video.title}" class="video-thumbnail" 
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22180%22%3E%3Crect fill=%22%232d2d2d%22 width=%22300%22 height=%22180%22/%3E%3Ctext fill=%22%23666%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'">
                <div class="video-info">
                    <div class="video-title">${video.title}</div>
                    <div class="video-meta">
                        <span>📺 ${video.platform}</span>
                        <span>⏱️ ${this.formatDuration(video.duration)}</span>
                    </div>
                    <div class="video-stats">
                        <div class="stat-item">
                            <span>👁️</span>
                            <span>${this.formatNumber(video.views)}</span>
                        </div>
                        <div class="stat-item">
                            <span>❤️</span>
                            <span>${this.formatNumber(video.likes)}</span>
                        </div>
                        <div class="stat-item">
                            <span class="viral-badge">${video.viral_score}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        // Add click handlers
        document.querySelectorAll('.video-card').forEach(card => {
            card.addEventListener('click', () => {
                const videoId = card.dataset.videoId;
                const video = videos.find(v => v.id === videoId);
                if (video) {
                    this.showVideoDetails(video);
                }
            });
        });
    }

    async showVideoDetails(video) {
        this.currentVideo = video;
        
        const modal = document.getElementById('video-modal');
        const title = document.getElementById('video-modal-title');
        const body = document.getElementById('video-modal-body');
        
        title.textContent = video.title;
        body.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div>
                    <img src="${video.thumbnail}" style="width: 100%; border-radius: 8px;" 
                         onerror="this.style.display='none'">
                </div>
                <div>
                    <p><strong>Платформа:</strong> ${video.platform}</p>
                    <p><strong>Канал:</strong> ${video.channel.name}</p>
                    <p><strong>Просмотры:</strong> ${this.formatNumber(video.views)}</p>
                    <p><strong>Лайки:</strong> ${this.formatNumber(video.likes)}</p>
                    <p><strong>Комментарии:</strong> ${this.formatNumber(video.comments)}</p>
                    <p><strong>Длительность:</strong> ${this.formatDuration(video.duration)}</p>
                    <p><strong>Viral Score:</strong> ${video.viral_score}%</p>
                    <p><strong>Дата:</strong> ${this.formatDate(video.published_date)}</p>
                    <p><strong>URL:</strong> <a href="${video.url}" target="_blank" style="color: #3b82f6;">Открыть</a></p>
                </div>
            </div>
            <div style="margin-top: 16px;">
                <p><strong>Описание:</strong></p>
                <p style="color: #a0a0a0; margin-top: 8px;">${video.description || 'Нет описания'}</p>
            </div>
        `;
        
        modal.classList.add('active');
    }

    async downloadVideo(video) {
        try {
            this.showNotification('Загрузка', 'Начинаем загрузку видео...', 'success');
            
            const data = await this.apiCall('/api/download', 'POST', {
                url: video.url,
                platform: video.platform
            });
            
            if (data.success) {
                this.showNotification('Успех', 'Видео успешно загружено', 'success');
                document.getElementById('video-modal').classList.remove('active');
            } else {
                this.showNotification('Ошибка', data.error || 'Не удалось загрузить видео', 'error');
            }
        } catch (error) {
            this.showNotification('Ошибка загрузки', error.message, 'error');
        }
    }

    // ===== AI Analyze =====
    
    async analyzeVideo() {
        const btn = document.getElementById('analyze-btn');
        btn.classList.add('loading');
        btn.disabled = true;

        try {
            const videoData = document.getElementById('video_data').value;
            const prompt = document.getElementById('analyze_prompt').value;

            let parsedData;
            try {
                parsedData = JSON.parse(videoData);
            } catch {
                parsedData = { description: videoData };
            }

            const data = await this.apiCall('/api/analyze', 'POST', {
                video_data: parsedData,
                prompt: prompt || undefined
            });

            const resultDiv = document.getElementById('analyze-result');
            const outputDiv = document.getElementById('analyze-output');
            
            if (data.success) {
                resultDiv.style.display = 'block';
                outputDiv.textContent = data.analysis || JSON.stringify(data, null, 2);
                this.showNotification('Анализ завершен', 'AI анализ выполнен успешно', 'success');
            } else {
                throw new Error(data.error || 'Ошибка анализа');
            }
        } catch (error) {
            this.showNotification('Ошибка анализа', error.message, 'error');
        } finally {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    }

    // ===== Config =====
    
    async loadConfig() {
        try {
            const data = await this.apiCall('/api/config/get');
            this.config = data;
            this.populateConfigForm();
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }

    async loadSettings() {
        await this.loadConfig();
    }

    populateConfigForm() {
        const c = this.config;
        
        // Search
        if (c.search) {
            document.getElementById('config-max-results').value = c.search.max_results || 10;
            document.getElementById('config-date-range').value = c.search.date_range || 'all';
            document.getElementById('config-min-views').value = c.search.min_views || 1000;
            document.getElementById('config-min-engagement').value = c.search.min_engagement || 5;
        }

        // AI
        if (c.ai) {
            document.getElementById('config-ai-timeout').value = c.ai.timeout || 30;
            document.getElementById('config-ai-retries').value = c.ai.max_retries || 3;
            document.getElementById('config-ai-cache').checked = c.ai.cache_enabled !== false;
        }

        // Download
        if (c.download) {
            document.getElementById('config-video-quality').value = c.download.video_quality || 'best';
            document.getElementById('config-max-size').value = c.download.max_file_size || 100;
            document.getElementById('config-subtitles').checked = c.download.subtitles === true;
            document.getElementById('config-thumbnail').checked = c.download.thumbnail !== false;
        }

        // Processing
        if (c.processing) {
            document.getElementById('config-clip-duration').value = c.processing.clip_duration || 30;
            document.getElementById('config-clips-per-video').value = c.processing.clips_per_video || 3;
            document.getElementById('config-video-bitrate').value = c.processing.video_bitrate || 2500;
            document.getElementById('config-auto-crop').checked = c.processing.auto_crop !== false;
            document.getElementById('config-filter-duplicates').checked = c.processing.filter_duplicates !== false;
        }
    }

    collectConfigFromForm() {
        return {
            search: {
                max_results: parseInt(document.getElementById('config-max-results').value),
                date_range: document.getElementById('config-date-range').value,
                min_views: parseInt(document.getElementById('config-min-views').value),
                min_engagement: parseFloat(document.getElementById('config-min-engagement').value)
            },
            ai: {
                timeout: parseInt(document.getElementById('config-ai-timeout').value),
                max_retries: parseInt(document.getElementById('config-ai-retries').value),
                cache_enabled: document.getElementById('config-ai-cache').checked,
                providers: this.config.ai?.providers || {}
            },
            download: {
                video_quality: document.getElementById('config-video-quality').value,
                max_file_size: parseInt(document.getElementById('config-max-size').value),
                subtitles: document.getElementById('config-subtitles').checked,
                thumbnail: document.getElementById('config-thumbnail').checked,
                methods: this.config.download?.methods || {},
                path: this.config.download?.path || 'downloads',
                proxy: this.config.download?.proxy || { enabled: false, url: '' }
            },
            processing: {
                clip_duration: parseInt(document.getElementById('config-clip-duration').value),
                clips_per_video: parseInt(document.getElementById('config-clips-per-video').value),
                output_format: this.config.processing?.output_format || 'mp4',
                video_bitrate: parseInt(document.getElementById('config-video-bitrate').value),
                auto_crop: document.getElementById('config-auto-crop').checked,
                add_watermark: this.config.processing?.add_watermark || false,
                filter_duplicates: document.getElementById('config-filter-duplicates').checked,
                filter_low_quality: this.config.processing?.filter_low_quality !== false,
                exclude_keywords: this.config.processing?.exclude_keywords || []
            },
            scenarios: this.config.scenarios || {}
        };
    }

    async saveConfig() {
        const btn = document.getElementById('save-config-btn');
        btn.classList.add('loading');
        btn.disabled = true;

        try {
            const newConfig = this.collectConfigFromForm();
            const data = await this.apiCall('/api/config/save', 'POST', newConfig);
            
            if (data.success) {
                this.config = newConfig;
                this.showNotification('Успех', 'Настройки сохранены', 'success');
            } else {
                throw new Error(data.error || 'Не удалось сохранить');
            }
        } catch (error) {
            this.showNotification('Ошибка сохранения', error.message, 'error');
        } finally {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    }

    async resetConfig() {
        // Reload default config from server
        await this.loadConfig();
        this.showNotification('Сброшено', 'Настройки сброшены к значениям по умолчанию', 'success');
    }

    // ===== Files =====
    
    async loadFiles() {
        try {
            const data = await this.apiCall('/api/files/list');
            this.renderFiles(data.files);
        } catch (error) {
            console.error('Failed to load files:', error);
        }
    }

    renderFiles(files) {
        const container = document.getElementById('files-list');
        
        if (!files || files.length === 0) {
            container.innerHTML = '<p class="empty-state">Нет файлов</p>';
            return;
        }

        container.innerHTML = files.map(file => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon">📹</div>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <div class="file-meta">
                            ${this.formatFileSize(file.size)} • ${this.formatDate(file.modified * 1000)}
                        </div>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-secondary btn-sm" onclick="app.deleteFile('${file.name}')">
                        🗑️ Удалить
                    </button>
                </div>
            </div>
        `).join('');
    }

    async deleteFile(filename) {
        if (!confirm(`Удалить файл ${filename}?`)) {
            return;
        }

        try {
            const data = await this.apiCall(`/api/files/delete/${encodeURIComponent(filename)}`, 'DELETE');
            
            if (data.success) {
                this.showNotification('Успех', data.message, 'success');
                await this.loadFiles();
            } else {
                throw new Error(data.error || 'Не удалось удалить');
            }
        } catch (error) {
            this.showNotification('Ошибка удаления', error.message, 'error');
        }
    }

    // ===== Status =====
    
    async loadStatus() {
        try {
            const data = await this.apiCall('/api/status');
            this.renderStatus(data);
        } catch (error) {
            console.error('Failed to load status:', error);
        }
    }

    renderStatus(data) {
        // Downloaders
        const downloadersContainer = document.getElementById('downloaders-status');
        if (data.downloaders && data.downloaders.length > 0) {
            downloadersContainer.innerHTML = data.downloaders.map(d => `
                <div class="status-item">
                    <div class="status-name">${d.name}</div>
                    <div class="status-badge ${d.available ? 'online' : 'offline'}">
                        ${d.available ? 'Доступен' : 'Недоступен'}
                    </div>
                </div>
            `).join('');
        } else {
            downloadersContainer.innerHTML = '<p class="empty-state">Загрузчики не настроены</p>';
        }

        // AI Providers
        const aiContainer = document.getElementById('ai-status');
        if (data.ai_providers && data.ai_providers.length > 0) {
            aiContainer.innerHTML = data.ai_providers.map(p => `
                <div class="status-item">
                    <div class="status-name">${p.name}</div>
                    <div class="status-badge ${p.available ? 'online' : 'offline'}">
                        ${p.available ? 'Доступен' : 'Недоступен'}
                    </div>
                </div>
            `).join('');
        } else {
            aiContainer.innerHTML = '<p class="empty-state">AI провайдеры не настроены</p>';
        }
    }

    async checkBackendStatus() {
        try {
            await this.apiCall('/api/status');
            this.updateStatusIndicator(true);
        } catch {
            this.updateStatusIndicator(false);
        }
    }

    updateStatusIndicator(online) {
        const dot = document.querySelector('.status-dot');
        const text = dot.nextElementSibling;
        
        if (online) {
            dot.classList.add('online');
            text.textContent = 'Backend активен';
        } else {
            dot.classList.remove('online');
            text.textContent = 'Backend недоступен';
        }
    }

    // ===== Presets =====
    
    showSavePresetModal() {
        document.getElementById('preset-modal').classList.add('active');
        document.getElementById('preset-name').value = '';
    }

    async showLoadPresetModal() {
        try {
            const data = await this.apiCall('/api/filters/list');
            this.presets = data.presets || [];
            this.renderPresetsList();
            document.getElementById('load-preset-modal').classList.add('active');
        } catch (error) {
            this.showNotification('Ошибка загрузки', error.message, 'error');
        }
    }

    renderPresetsList() {
        const container = document.getElementById('presets-list');
        
        if (!this.presets || this.presets.length === 0) {
            container.innerHTML = '<p class="empty-state">Нет сохраненных пресетов</p>';
            return;
        }

        container.innerHTML = this.presets.map(preset => `
            <div class="preset-item" data-preset-id="${preset.id}">
                <div>
                    <div class="preset-name">${preset.name}</div>
                    <div class="preset-date">${this.formatDate(preset.created_at)}</div>
                </div>
                <div class="preset-actions">
                    <button class="btn btn-primary btn-sm" onclick="app.loadPreset('${preset.id}')">
                        Загрузить
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="app.deletePreset('${preset.id}')">
                        Удалить
                    </button>
                </div>
            </div>
        `).join('');
    }

    async savePreset() {
        const name = document.getElementById('preset-name').value.trim();
        
        if (!name) {
            this.showNotification('Ошибка', 'Введите название пресета', 'warning');
            return;
        }

        const formData = new FormData(document.getElementById('search-form'));
        const filters = {};
        
        for (let [key, value] of formData.entries()) {
            filters[key] = value;
        }

        try {
            const data = await this.apiCall('/api/filters/save', 'POST', {
                name,
                filters
            });
            
            if (data.success) {
                this.showNotification('Успех', 'Пресет сохранен', 'success');
                document.getElementById('preset-modal').classList.remove('active');
            } else {
                throw new Error(data.error || 'Не удалось сохранить');
            }
        } catch (error) {
            this.showNotification('Ошибка сохранения', error.message, 'error');
        }
    }

    loadPreset(presetId) {
        const preset = this.presets.find(p => p.id === presetId);
        if (!preset) return;

        const form = document.getElementById('search-form');
        const filters = preset.filters;

        for (let key in filters) {
            const input = form.elements[key];
            if (input) {
                input.value = filters[key];
            }
        }

        document.getElementById('load-preset-modal').classList.remove('active');
        this.showNotification('Загружено', `Пресет "${preset.name}" загружен`, 'success');
    }

    async deletePreset(presetId) {
        if (!confirm('Удалить этот пресет?')) {
            return;
        }

        try {
            const data = await this.apiCall(`/api/filters/delete/${presetId}`, 'DELETE');
            
            if (data.success) {
                this.presets = this.presets.filter(p => p.id !== presetId);
                this.renderPresetsList();
                this.showNotification('Успех', 'Пресет удален', 'success');
            } else {
                throw new Error(data.error || 'Не удалось удалить');
            }
        } catch (error) {
            this.showNotification('Ошибка удаления', error.message, 'error');
        }
    }

    // ===== Utilities =====
    
    showNotification(title, message, type = 'success') {
        const container = document.getElementById('notifications');
        const id = 'notif-' + Date.now();
        
        const notif = document.createElement('div');
        notif.id = id;
        notif.className = `notification ${type}`;
        notif.innerHTML = `
            <div class="notification-icon">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️'}
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
        `;
        
        container.appendChild(notif);
        
        setTimeout(() => {
            notif.remove();
        }, 5000);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    formatFileSize(bytes) {
        if (bytes >= 1024 * 1024 * 1024) {
            return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
        } else if (bytes >= 1024 * 1024) {
            return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        } else if (bytes >= 1024) {
            return (bytes / 1024).toFixed(2) + ' KB';
        }
        return bytes + ' B';
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Только что';
        if (minutes < 60) return `${minutes} мин назад`;
        if (hours < 24) return `${hours} ч назад`;
        if (days < 7) return `${days} дн назад`;
        
        return date.toLocaleDateString('ru-RU');
    }

    getOperationTypeLabel(type) {
        const labels = {
            'download': 'Загрузка видео',
            'analyze': 'AI анализ',
            'process': 'Обработка видео'
        };
        return labels[type] || type;
    }
}

// Initialize app
const app = new ReShortsApp();

// Make app available globally for onclick handlers
window.app = app;
