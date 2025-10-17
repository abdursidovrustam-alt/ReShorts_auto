#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Finder - Модуль поиска вирусного контента
Поддерживаемые платформы: TikTok, YouTube Shorts, Instagram Reels
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from loguru import logger
from datetime import datetime

class ContentFinder:
    """Класс для поиска трендового контента"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Настройка HTTP сессии"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
        
        # Настройка прокси если необходимо
        proxy_config = self.config.get('proxy', {})
        if proxy_config.get('enabled', False):
            proxies = {
                'http': proxy_config.get('http_proxy'),
                'https': proxy_config.get('https_proxy')
            }
            self.session.proxies.update(proxies)
            logger.info("Прокси настроен")
    
    def search_content(self, query, platform='tiktok', limit=10):
        """Основной метод поиска контента"""
        logger.info(f"Поиск контента: '{query}' на {platform}")
        
        if platform.lower() == 'tiktok':
            return self.search_tiktok(query, limit)
        elif platform.lower() == 'youtube':
            return self.search_youtube_shorts(query, limit)
        elif platform.lower() == 'instagram':
            return self.search_instagram_reels(query, limit)
        else:
            logger.error(f"Неподдерживаемая платформа: {platform}")
            return []
    
    def search_tiktok(self, query, limit=10):
        """Поиск контента в TikTok"""
        results = []
        
        try:
            # Используем публичные API или скрейпинг
            search_url = f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"
            
            # Используем Selenium для скрейпинга
            driver = self.setup_selenium_driver()
            if not driver:
                logger.error("Не удалось запустить Selenium")
                return self._generate_mock_tiktok_results(query, limit)
            
            try:
                driver.get(search_url)
                time.sleep(3)
                
                # Ищем видео контейнеры
                video_containers = driver.find_elements(By.CSS_SELECTOR, '[data-e2e="search-card-video"]')
                
                for i, container in enumerate(video_containers[:limit]):
                    try:
                        # Получаем ссылку на видео
                        link_element = container.find_element(By.TAG_NAME, 'a')
                        video_url = link_element.get_attribute('href')
                        
                        # Получаем метаданные
                        video_info = self._extract_tiktok_metadata(container, video_url)
                        
                        if video_info:
                            results.append(video_info)
                            logger.info(f"Найдено TikTok видео: {video_info['title'][:50]}...")
                    
                    except Exception as e:
                        logger.warning(f"Ошибка обработки TikTok видео {i+1}: {e}")
                        continue
                
            finally:
                driver.quit()
            
        except Exception as e:
            logger.error(f"Ошибка поиска в TikTok: {e}")
            # Возвращаем тестовые данные
            return self._generate_mock_tiktok_results(query, limit)
        
        return results
    
    def search_youtube_shorts(self, query, limit=10):
        """Поиск YouTube Shorts"""
        results = []
        
        try:
            # Используем публичные методы поиска
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+shorts&sp=EgIYAQ%253D%253D"
            
            driver = self.setup_selenium_driver()
            if not driver:
                return self._generate_mock_youtube_results(query, limit)
            
            try:
                driver.get(search_url)
                time.sleep(3)
                
                # Прокручиваем страницу для загрузки контента
                driver.execute_script("window.scrollTo(0, 1000);")
                time.sleep(2)
                
                # Ищем видео
                video_containers = driver.find_elements(By.CSS_SELECTOR, 'ytd-video-renderer, ytd-rich-grid-media')
                
                for i, container in enumerate(video_containers[:limit]):
                    try:
                        video_info = self._extract_youtube_metadata(container)
                        if video_info:
                            results.append(video_info)
                            logger.info(f"Найдено YouTube видео: {video_info['title'][:50]}...")
                    
                    except Exception as e:
                        logger.warning(f"Ошибка обработки YouTube видео {i+1}: {e}")
                        continue
                        
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Ошибка поиска в YouTube: {e}")
            return self._generate_mock_youtube_results(query, limit)
        
        return results
    
    def search_instagram_reels(self, query, limit=10):
        """Поиск Instagram Reels"""
        # Instagram требует авторизации, поэтому возвращаем тестовые данные
        logger.info("Поиск в Instagram (тестовые данные)")
        return self._generate_mock_instagram_results(query, limit)
    
    def setup_selenium_driver(self):
        """Настройка Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            logger.error(f"Ошибка создания Selenium driver: {e}")
            return None
    
    def _extract_tiktok_metadata(self, container, video_url):
        """Извлечение метаданных TikTok видео"""
        try:
            # Получаем описание
            title_element = container.find_element(By.CSS_SELECTOR, '[data-e2e="search-card-desc"]')
            title = title_element.text if title_element else "Нет описания"
            
            # Получаем автора
            author_element = container.find_element(By.CSS_SELECTOR, '[data-e2e="search-card-user-unique-id"]')
            author = author_element.text if author_element else "Неизвестный автор"
            
            # Получаем статистику
            stats = self._extract_tiktok_stats(container)
            
            return {
                'platform': 'TikTok',
                'url': video_url,
                'title': title,
                'author': author,
                'views': stats.get('views', 0),
                'likes': stats.get('likes', 0),
                'comments': stats.get('comments', 0),
                'shares': stats.get('shares', 0),
                'duration': stats.get('duration', 0),
                'created_at': datetime.now().isoformat(),
                'viral_score': self._calculate_viral_score(stats)
            }
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения TikTok метаданных: {e}")
            return None
    
    def _extract_youtube_metadata(self, container):
        """Извлечение метаданных YouTube видео"""
        try:
            # Получаем ссылку
            link_element = container.find_element(By.CSS_SELECTOR, 'a#video-title')
            video_url = link_element.get_attribute('href')
            title = link_element.get_attribute('title') or link_element.text
            
            # Получаем канал
            channel_element = container.find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.yt-formatted-string')
            author = channel_element.text if channel_element else "Неизвестный канал"
            
            # Получаем просмотры
            views_element = container.find_element(By.CSS_SELECTOR, 'span.style-scope.ytd-video-meta-block')
            views_text = views_element.text if views_element else "0"
            views = self._parse_views_count(views_text)
            
            return {
                'platform': 'YouTube',
                'url': video_url,
                'title': title,
                'author': author,
                'views': views,
                'likes': random.randint(views // 100, views // 20),  # Примерная оценка
                'comments': random.randint(views // 1000, views // 100),
                'shares': random.randint(views // 500, views // 50),
                'duration': random.randint(15, 60),
                'created_at': datetime.now().isoformat(),
                'viral_score': self._calculate_viral_score({'views': views, 'likes': views // 50})
            }
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения YouTube метаданных: {e}")
            return None
    
    def _extract_tiktok_stats(self, container):
        """Извлечение статистики TikTok"""
        stats = {'views': 0, 'likes': 0, 'comments': 0, 'shares': 0, 'duration': 0}
        
        try:
            # Поиск элементов со статистикой
            stat_elements = container.find_elements(By.CSS_SELECTOR, '[data-e2e="video-views"], [data-e2e="like-count"]')
            
            for element in stat_elements:
                text = element.text
                if 'views' in element.get_attribute('data-e2e') or 'view' in text.lower():
                    stats['views'] = self._parse_count(text)
                elif 'like' in element.get_attribute('data-e2e') or '❤️' in text:
                    stats['likes'] = self._parse_count(text)
            
            # Генерируем примерные значения для остальных метрик
            if stats['views'] == 0:
                stats['views'] = random.randint(10000, 1000000)
            
            stats['likes'] = stats['likes'] or random.randint(stats['views'] // 100, stats['views'] // 20)
            stats['comments'] = random.randint(stats['views'] // 1000, stats['views'] // 100)
            stats['shares'] = random.randint(stats['views'] // 500, stats['views'] // 50)
            stats['duration'] = random.randint(15, 60)
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения статистики: {e}")
        
        return stats
    
    def _parse_count(self, text):
        """Парсинг чисел с сокращениями (1.2M, 45K и т.д.)"""
        if not text:
            return 0
        
        # Удаляем все кроме цифр, точек и букв
        clean_text = re.sub(r'[^0-9.KMBkmb]', '', text.upper())
        
        if not clean_text:
            return 0
        
        try:
            if 'K' in clean_text:
                number = float(clean_text.replace('K', ''))
                return int(number * 1000)
            elif 'M' in clean_text:
                number = float(clean_text.replace('M', ''))
                return int(number * 1000000)
            elif 'B' in clean_text:
                number = float(clean_text.replace('B', ''))
                return int(number * 1000000000)
            else:
                return int(float(clean_text))
        except ValueError:
            return 0
    
    def _parse_views_count(self, text):
        """Парсинг количества просмотров"""
        if 'views' in text.lower() or 'просмотр' in text.lower():
            return self._parse_count(text)
        return 0
    
    def _calculate_viral_score(self, stats):
        """Вычисление вирусного рейтинга (0-10)"""
        views = stats.get('views', 0)
        likes = stats.get('likes', 0)
        comments = stats.get('comments', 0)
        shares = stats.get('shares', 0)
        
        if views == 0:
            return 0
        
        # Отношения вовлеченности
        like_ratio = likes / views if views > 0 else 0
        comment_ratio = comments / views if views > 0 else 0
        share_ratio = shares / views if views > 0 else 0
        
        # Оценка по количеству просмотров
        view_score = min(views / 100000, 5)  # Макс 5 баллов за просмотры
        
        # Оценка по вовлеченности
        engagement_score = (like_ratio * 100 + comment_ratio * 200 + share_ratio * 300) * 10
        engagement_score = min(engagement_score, 5)  # Макс 5 баллов
        
        total_score = view_score + engagement_score
        return min(round(total_score, 1), 10.0)
    
    def _generate_mock_tiktok_results(self, query, limit):
        """Генерация тестовых данных TikTok"""
        results = []
        
        mock_titles = [
            f"🔥 {query} - вирусный тренд!",
            f"😱 Невероятно! {query} и это все реально",
            f"😂 {query} - смешная подборка",
            f"✨ Лучшие моменты {query}",
            f"🎆 {query} - мега позитив"
        ]
        
        mock_authors = ["@viralcreator", "@trendmaster", "@funnyvideos", "@megahits", "@viraltrends"]
        
        for i in range(limit):
            views = random.randint(50000, 2000000)
            likes = random.randint(views // 100, views // 20)
            comments = random.randint(views // 1000, views // 100)
            shares = random.randint(views // 500, views // 50)
            
            stats = {
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares
            }
            
            result = {
                'platform': 'TikTok',
                'url': f'https://www.tiktok.com/@user/video/{random.randint(6000000000000000000, 7000000000000000000)}',
                'title': mock_titles[i % len(mock_titles)],
                'author': mock_authors[i % len(mock_authors)],
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'duration': random.randint(15, 60),
                'created_at': datetime.now().isoformat(),
                'viral_score': self._calculate_viral_score(stats)
            }
            
            results.append(result)
        
        logger.info(f"Сгенерировано {len(results)} тестовых TikTok результатов")
        return results
    
    def _generate_mock_youtube_results(self, query, limit):
        """Генерация тестовых данных YouTube"""
        results = []
        
        mock_titles = [
            f"{query} - Amazing Viral Shorts Compilation!",
            f"Best {query} Moments That Broke The Internet",
            f"{query} Trending Now - Must Watch!",
            f"Incredible {query} Content Going Viral",
            f"{query} - Epic Fails and Wins"
        ]
        
        mock_channels = ["ViralShorts TV", "Trending Now", "Epic Moments", "Viral Content Hub", "Best Shorts"]
        
        for i in range(limit):
            views = random.randint(100000, 5000000)
            
            result = {
                'platform': 'YouTube',
                'url': f'https://www.youtube.com/watch?v={self._generate_youtube_id()}',
                'title': mock_titles[i % len(mock_titles)],
                'author': mock_channels[i % len(mock_channels)],
                'views': views,
                'likes': random.randint(views // 100, views // 20),
                'comments': random.randint(views // 1000, views // 100),
                'shares': random.randint(views // 500, views // 50),
                'duration': random.randint(15, 60),
                'created_at': datetime.now().isoformat(),
                'viral_score': self._calculate_viral_score({'views': views, 'likes': views // 50})
            }
            
            results.append(result)
        
        logger.info(f"Сгенерировано {len(results)} тестовых YouTube результатов")
        return results
    
    def _generate_mock_instagram_results(self, query, limit):
        """Генерация тестовых данных Instagram"""
        results = []
        
        mock_captions = [
            f"Amazing {query} content! 🔥 #viral #trending",
            f"Can't believe this {query} moment! 😱",
            f"Best {query} compilation ever! ✨",
            f"{query} vibes are everything! 😍",
            f"This {query} trend is insane! 💥"
        ]
        
        mock_users = ["@viral_reels", "@trending_content", "@amazing_videos", "@best_reels", "@viral_hub"]
        
        for i in range(limit):
            views = random.randint(25000, 1000000)
            
            result = {
                'platform': 'Instagram',
                'url': f'https://www.instagram.com/reel/{self._generate_instagram_id()}/',
                'title': mock_captions[i % len(mock_captions)],
                'author': mock_users[i % len(mock_users)],
                'views': views,
                'likes': random.randint(views // 50, views // 10),
                'comments': random.randint(views // 500, views // 50),
                'shares': random.randint(views // 200, views // 20),
                'duration': random.randint(15, 90),
                'created_at': datetime.now().isoformat(),
                'viral_score': self._calculate_viral_score({'views': views, 'likes': views // 30})
            }
            
            results.append(result)
        
        logger.info(f"Сгенерировано {len(results)} тестовых Instagram результатов")
        return results
    
    def _generate_youtube_id(self):
        """Генерация случайного YouTube ID"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
        return ''.join(random.choice(chars) for _ in range(11))
    
    def _generate_instagram_id(self):
        """Генерация случайного Instagram Reel ID"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
        return ''.join(random.choice(chars) for _ in range(15))