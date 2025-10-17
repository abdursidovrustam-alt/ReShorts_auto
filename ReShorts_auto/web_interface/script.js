// Главный JavaScript файл для Viral Shorts Master

class ViralShortsApp {
    constructor() {
        this.isProcessing = false;
        this.currentProgress = 0;
        this.processedVideos = 0;
        this.downloadedVideos = 0;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStatistics();
        this.checkApiSettings();
    }

    bindEvents() {
        // Обработка формы поиска
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startProcessing();
        });

        // Обработка кнопки скачивания всех видео
        document.getElementById('downloadAllBtn').addEventListener('click', () => {
            this.downloadAllVideos();
        });

        // Закрытие модального окна
        document.querySelector('.close').addEventListener('click', () => {
            this.closeModal();
        });

        // Закрытие модального окна при клике вне его
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('apiModal');
            if (e.target === modal) {
                this.closeModal();
            }
        });
    }

    async startProcessing() {
        if (this.isProcessing) return;

        this.isProcessing = true;
        const startBtn = document.getElementById('startBtn');
        startBtn.disabled = true;
        startBtn.textContent = '⏳ Обрабатываем...';

        // Показываем панель прогресса
        this.showProgressPanel();
        
        // Получаем данные формы
        const formData = this.getFormData();
        
        try {
            // Отправляем запрос на бэкенд
            await this.processVideos(formData);
        } catch (error) {
            this.showError('Произошла ошибка при обработке: ' + error.message);
        } finally {
            this.isProcessing = false;
            startBtn.disabled = false;
            startBtn.textContent = '🚀 Начать поиск и обработку';
        }
    }

    getFormData() {
        return {
            theme: document.getElementById('theme').value,
            platform: document.getElementById('platform').value,
            videoCount: parseInt(document.getElementById('videoCount').value),
            uniqueness: document.getElementById('uniqueness').value
        };
    }

    async processVideos(formData) {
        const steps = [
            'Поиск вирусных видео...',
            'Анализ контента...',
            'Уникализация видео...',
            'Сохранение результатов...'
        ];

        for (let i = 0; i < steps.length; i++) {
            this.updateProgress((i + 1) / steps.length * 100, steps[i]);
            
            // Симуляция обработки (в реальном приложении здесь будут API вызовы)
            await this.delay(2000);
            
            if (i === 0) {
                // Поиск видео
                await this.searchVideos(formData);
            } else if (i === 1) {
                // Анализ
                await this.analyzeVideos(formData);
            } else if (i === 2) {
                // Уникализация
                await this.uniqualizeVideos(formData);
            } else if (i === 3) {
                // Сохранение
                await this.saveResults(formData);
            }
        }

        this.showResults();
    }

    async searchVideos(formData) {
        // В реальном приложении здесь будет API вызов
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка поиска видео');
            }
            
            const data = await response.json();
            this.updateCurrentStep(`Найдено ${data.found} видео по теме "${formData.theme}"`);
        } catch (error) {
            console.log('Работаем в демо режиме - API недоступно');
            this.updateCurrentStep(`Найдено ${formData.videoCount} видео по теме "${formData.theme}"`);
        }
    }

    async analyzeVideos(formData) {
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка анализа видео');
            }
            
            this.updateCurrentStep('Анализ завершен. Определены лучшие кандидаты.');
        } catch (error) {
            console.log('Работаем в демо режиме - API недоступно');
            this.updateCurrentStep('Анализ завершен. Определены лучшие кандидаты.');
        }
    }

    async uniqualizeVideos(formData) {
        try {
            const response = await fetch('/api/uniqualize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка уникализации видео');
            }
            
            this.updateCurrentStep(`Уникализация завершена (уровень: ${formData.uniqueness})`);
        } catch (error) {
            console.log('Работаем в демо режиме - API недоступно');
            this.updateCurrentStep(`Уникализация завершена (уровень: ${formData.uniqueness})`);
        }
    }

    async saveResults(formData) {
        try {
            const response = await fetch('/api/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка сохранения результатов');
            }
            
            this.updateCurrentStep('Все видео сохранены и готовы к использованию!');
        } catch (error) {
            console.log('Работаем в демо режиме - API недоступно');
            this.updateCurrentStep('Все видео сохранены и готовы к использованию!');
        }
    }

    showProgressPanel() {
        document.getElementById('progressPanel').style.display = 'block';
        document.getElementById('resultsPanel').style.display = 'none';
    }

    updateProgress(percentage, text) {
        this.currentProgress = percentage;
        document.getElementById('progressFill').style.width = percentage + '%';
        document.getElementById('progressText').textContent = text;
    }

    updateCurrentStep(step) {
        document.getElementById('currentStep').textContent = step;
    }

    showResults() {
        document.getElementById('progressPanel').style.display = 'none';
        document.getElementById('resultsPanel').style.display = 'block';
        
        // Создаем демо результаты
        this.createDemoResults();
        
        // Обновляем статистику
        this.updateStatistics();
    }

    createDemoResults() {
        const resultsContent = document.getElementById('resultsContent');
        const formData = this.getFormData();
        
        let resultsHTML = '';
        
        for (let i = 1; i <= Math.min(formData.videoCount, 5); i++) {
            resultsHTML += `
                <div class="video-result">
                    <h3>📹 Видео ${i}: "${formData.theme} - Уникальная версия ${i}"</h3>
                    <p><strong>Источник:</strong> ${formData.platform}</p>
                    <p><strong>Длительность:</strong> ${Math.floor(Math.random() * 30) + 15} сек</p>
                    <p><strong>Уровень уникализации:</strong> ${formData.uniqueness}</p>
                    <p><strong>Статус:</strong> ✅ Готово к использованию</p>
                    <div class="video-actions">
                        <button class="btn btn-secondary" onclick="app.downloadVideo(${i})">
                            📥 Скачать
                        </button>
                        <button class="btn btn-secondary" onclick="app.previewVideo(${i})">
                            👁️ Предпросмотр
                        </button>
                        <button class="btn btn-secondary" onclick="app.editVideo(${i})">
                            ✏️ Редактировать
                        </button>
                    </div>
                </div>
            `;
        }
        
        resultsContent.innerHTML = resultsHTML;
        document.getElementById('downloadAllBtn').style.display = 'block';
    }

    downloadVideo(id) {
        // В реальном приложении здесь будет скачивание файла
        alert(`Скачивание видео ${id} (демо версия - файл будет доступен после настройки backend)`);
        this.downloadedVideos++;
        this.updateStatistics();
    }

    previewVideo(id) {
        alert(`Предпросмотр видео ${id} (демо версия)`);
    }

    editVideo(id) {
        alert(`Редактирование видео ${id} (демо версия)`);
    }

    downloadAllVideos() {
        alert('Скачивание всех видео (демо версия - функция будет доступна после настройки backend)');
    }

    updateStatistics() {
        this.processedVideos = Math.min(this.processedVideos + 1, 999);
        const successRate = this.processedVideos > 0 ? Math.round((this.downloadedVideos / this.processedVideos) * 100) : 0;
        
        document.getElementById('totalProcessed').textContent = this.processedVideos;
        document.getElementById('totalDownloaded').textContent = this.downloadedVideos;
        document.getElementById('successRate').textContent = successRate + '%';
    }

    loadStatistics() {
        // Загрузка статистики из localStorage или API
        const stats = localStorage.getItem('viralShortsStats');
        if (stats) {
            const parsed = JSON.parse(stats);
            this.processedVideos = parsed.processed || 0;
            this.downloadedVideos = parsed.downloaded || 0;
            this.updateStatistics();
        }
    }

    saveStatistics() {
        const stats = {
            processed: this.processedVideos,
            downloaded: this.downloadedVideos
        };
        localStorage.setItem('viralShortsStats', JSON.stringify(stats));
    }

    checkApiSettings() {
        // Проверяем, настроены ли API ключи
        const apiSettings = localStorage.getItem('viralShortsApi');
        if (!apiSettings) {
            setTimeout(() => {
                this.showModal();
            }, 2000);
        }
    }

    showModal() {
        document.getElementById('apiModal').style.display = 'block';
    }

    closeModal() {
        document.getElementById('apiModal').style.display = 'none';
    }

    showError(message) {
        alert('Ошибка: ' + message);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Функции для настройки API
function openApiSettings() {
    alert('Настройки API будут доступны в файле config.json после полной установки проекта');
    app.closeModal();
}

// Инициализация приложения
const app = new ViralShortsApp();

// Сохранение статистики при закрытии страницы
window.addEventListener('beforeunload', () => {
    app.saveStatistics();
});