#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Продвинутый модуль обработки и уникализации видео
Объединяет лучшие практики из топовых GitHub проектов

Автор: MiniMax Agent
Дата: 2025-10-17
Вдохновлен: ShortGPT, auto-yt-shorts, short-video-maker
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Callable
from datetime import datetime
import random
import json
import logging
from dataclasses import dataclass, asdict
import tempfile
import shutil
import subprocess

# Видео обработка
try:
    # Попытка импорта для новой версии moviepy (2.x)
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeVideoClip, 
        CompositeAudioClip, TextClip, ColorClip, 
        concatenate_videoclips, vfx, afx
    )
except ImportError:
    # Для старой версии moviepy (1.x)
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, CompositeVideoClip, 
        CompositeAudioClip, TextClip, ColorClip, 
        concatenate_videoclips, vfx, afx
    )

# Обработка изображений
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from scipy import ndimage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Результат обработки видео"""
    success: bool
    input_file: str
    output_file: Optional[str] = None
    duration: float = 0.0
    size_mb: float = 0.0
    resolution: str = ""
    applied_effects: List[str] = None
    uniqueness_score: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.applied_effects is None:
            self.applied_effects = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdvancedVideoProcessor:
    """
    Продвинутый процессор видео с 25+ эффектами и уникализацией
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Инициализация процессора
        
        Args:
            config: Конфигурация процессора
        """
        self.config = config or {}
        
        # Директории
        self.output_dir = Path(self.config.get('output_dir', 'processed'))
        self.temp_dir = Path(self.config.get('temp_dir', 'tmp/video_processing'))
        self.cache_dir = Path(self.config.get('cache_dir', 'tmp/cache'))
        
        # Создание директорий
        for directory in [self.output_dir, self.temp_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Параметры обработки
        self.default_quality = self.config.get('quality', '720p')
        self.max_duration = self.config.get('max_duration', 60)
        self.target_fps = self.config.get('target_fps', 30)
        self.clear_metadata = self.config.get('clear_metadata', True)
        
        # Качество видео
        self.quality_presets = {
            '360p': {'height': 360, 'bitrate': '800k', 'audio_bitrate': '96k'},
            '480p': {'height': 480, 'bitrate': '1200k', 'audio_bitrate': '128k'},
            '720p': {'height': 720, 'bitrate': '2500k', 'audio_bitrate': '192k'},
            '1080p': {'height': 1080, 'bitrate': '5000k', 'audio_bitrate': '256k'},
        }
        
        # Доступные эффекты
        self.video_effects = {
            # Цветовые эффекты
            'brightness': self._effect_brightness,
            'contrast': self._effect_contrast,
            'saturation': self._effect_saturation,
            'hue': self._effect_hue,
            'temperature': self._effect_temperature,
            
            # Стилистические эффекты
            'sepia': self._effect_sepia,
            'grayscale': self._effect_grayscale,
            'vintage': self._effect_vintage,
            'cinematic': self._effect_cinematic,
            'neon': self._effect_neon,
            'retro': self._effect_retro,
            'cyberpunk': self._effect_cyberpunk,
            
            # Фильтры
            'blur': self._effect_blur,
            'sharpen': self._effect_sharpen,
            'edge_enhance': self._effect_edge_enhance,
            'emboss': self._effect_emboss,
            'noise': self._effect_noise,
            'film_grain': self._effect_film_grain,
            
            # Геометрические эффекты
            'vignette': self._effect_vignette,
            'fisheye': self._effect_fisheye,
            'chromatic_aberration': self._effect_chromatic_aberration,
            
            # Специальные эффекты
            'glitch': self._effect_glitch,
            'pixelate': self._effect_pixelate,
            'ascii': self._effect_ascii,
            'mirror_horizontal': self._effect_mirror_horizontal,
            'mirror_vertical': self._effect_mirror_vertical,
        }
        
        logger.info(f"🎬 Инициализирован AdvancedVideoProcessor с {len(self.video_effects)} эффектами")
    
    def process_video(
        self,
        input_file: str,
        effects: List[str] = None,
        options: Dict[str, Any] = None,
        output_file: str = None
    ) -> ProcessingResult:
        """
        Обработка видео с применением эффектов
        
        Args:
            input_file: Путь к входному видео
            effects: Список эффектов для применения
            options: Дополнительные опции обработки
            output_file: Путь к выходному файлу (опционально)
        
        Returns:
            ProcessingResult с результатами обработки
        """
        start_time = datetime.now()
        input_path = Path(input_file)
        
        if not input_path.exists():
            return ProcessingResult(
                success=False,
                input_file=input_file,
                error=f"Файл не найден: {input_file}"
            )
        
        logger.info(f"📹 Начало обработки: {input_path.name}")
        
        try:
            options = options or {}
            effects = effects or self._select_random_effects()
            
            # Генерация имени выходного файла
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"processed_{timestamp}_{input_path.stem}.mp4"
            else:
                output_file = Path(output_file)
            
            # Загрузка видео
            with VideoFileClip(str(input_file)) as video:
                original_duration = video.duration
                original_size = video.size
                
                # Обрезка длительности если необходимо
                if video.duration > self.max_duration:
                    logger.info(f"⏱️ Обрезка видео: {video.duration:.1f}с → {self.max_duration}с")
                    video = video.subclip(0, self.max_duration)
                
                # Применение эффектов
                processed_video = self._apply_effects_chain(video, effects, options)
                
                # Обработка аудио
                processed_video = self._process_audio(processed_video, options)
                
                # Добавление субтитров/текста
                if options.get('add_text'):
                    processed_video = self._add_text_overlay(processed_video, options)
                
                # Оптимизация качества
                processed_video = self._optimize_video(processed_video, options)
                
                # Сохранение
                quality = options.get('quality', self.default_quality)
                preset = self.quality_presets.get(quality, self.quality_presets['720p'])
                
                logger.info(f"💾 Сохранение: {output_file.name}")
                processed_video.write_videofile(
                    str(output_file),
                    codec='libx264',
                    audio_codec='aac',
                    bitrate=preset['bitrate'],
                    audio_bitrate=preset['audio_bitrate'],
                    fps=self.target_fps,
                    preset='medium',
                    threads=4,
                    verbose=False,
                    logger=None
                )
            
            # Очистка метаданных
            if self.clear_metadata:
                self._clear_file_metadata(output_file)
            
            # Расчет метрик
            processing_time = (datetime.now() - start_time).total_seconds()
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            uniqueness_score = self._calculate_uniqueness_score(effects, options)
            
            result = ProcessingResult(
                success=True,
                input_file=str(input_file),
                output_file=str(output_file),
                duration=original_duration,
                size_mb=round(file_size_mb, 2),
                resolution=f"{original_size[0]}x{original_size[1]}",
                applied_effects=effects,
                uniqueness_score=round(uniqueness_score, 3),
                processing_time=round(processing_time, 2),
                metadata={
                    'original_duration': original_duration,
                    'final_duration': min(original_duration, self.max_duration),
                    'quality': quality,
                    'fps': self.target_fps
                }
            )
            
            # Сохранение информации о обработке
            self._save_processing_info(result)
            
            logger.info(f"✅ Обработка завершена за {processing_time:.2f}с")
            logger.info(f"📊 Уникальность: {uniqueness_score:.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки: {e}", exc_info=True)
            return ProcessingResult(
                success=False,
                input_file=str(input_file),
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
    
    def batch_process(
        self,
        input_files: List[str],
        effects: List[str] = None,
        options: Dict[str, Any] = None,
        progress_callback: Callable[[int, int], None] = None
    ) -> List[ProcessingResult]:
        """
        Пакетная обработка видео
        
        Args:
            input_files: Список путей к входным видео
            effects: Эффекты для применения
            options: Опции обработки
            progress_callback: Функция обратного вызова для прогресса
        
        Returns:
            Список результатов обработки
        """
        logger.info(f"📦 Пакетная обработка {len(input_files)} видео")
        
        results = []
        for i, input_file in enumerate(input_files, 1):
            if progress_callback:
                progress_callback(i, len(input_files))
            
            logger.info(f"[{i}/{len(input_files)}] Обработка: {Path(input_file).name}")
            result = self.process_video(input_file, effects, options)
            results.append(result)
        
        # Статистика
        successful = sum(1 for r in results if r.success)
        total_time = sum(r.processing_time for r in results)
        
        logger.info(f"✅ Пакетная обработка завершена:")
        logger.info(f"   Успешно: {successful}/{len(input_files)}")
        logger.info(f"   Общее время: {total_time:.2f}с")
        
        return results
    
    def _apply_effects_chain(
        self,
        video: VideoFileClip,
        effects: List[str],
        options: Dict[str, Any]
    ) -> VideoFileClip:
        """Применение цепочки эффектов"""
        processed = video
        
        for effect_name in effects:
            if effect_name in self.video_effects:
                try:
                    logger.info(f"   🎨 Применяю эффект: {effect_name}")
                    effect_func = self.video_effects[effect_name]
                    processed = effect_func(processed, options)
                except Exception as e:
                    logger.warning(f"   ⚠️ Ошибка эффекта {effect_name}: {e}")
            else:
                logger.warning(f"   ⚠️ Неизвестный эффект: {effect_name}")
        
        return processed
    
    # ===========================================
    # ЦВЕТОВЫЕ ЭФФЕКТЫ
    # ===========================================
    
    def _effect_brightness(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Изменение яркости"""
        factor = options.get('brightness_factor', random.uniform(0.85, 1.15))
        
        def adjust(frame):
            return np.clip(frame * factor, 0, 255).astype(np.uint8)
        
        return video.fl_image(adjust)
    
    def _effect_contrast(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Изменение контрастности"""
        factor = options.get('contrast_factor', random.uniform(0.9, 1.3))
        
        def adjust(frame):
            mean = np.mean(frame)
            return np.clip((frame - mean) * factor + mean, 0, 255).astype(np.uint8)
        
        return video.fl_image(adjust)
    
    def _effect_saturation(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Изменение насыщенности"""
        factor = options.get('saturation_factor', random.uniform(0.8, 1.4))
        
        def adjust(frame):
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= factor
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        return video.fl_image(adjust)
    
    def _effect_hue(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Смещение оттенка"""
        shift = options.get('hue_shift', random.randint(-30, 30))
        
        def adjust(frame):
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.int16)
            hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
            return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        return video.fl_image(adjust)
    
    def _effect_temperature(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Цветовая температура (теплее/холоднее)"""
        temp = options.get('temperature', random.uniform(-0.1, 0.1))
        
        def adjust(frame):
            adjusted = frame.copy().astype(np.float32)
            if temp > 0:  # Теплее
                adjusted[:, :, 0] *= (1 + temp)  # Больше красного
                adjusted[:, :, 2] *= (1 - temp * 0.5)  # Меньше синего
            else:  # Холоднее
                adjusted[:, :, 0] *= (1 + temp)  # Меньше красного
                adjusted[:, :, 2] *= (1 - temp)  # Больше синего
            return np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return video.fl_image(adjust)
    
    # ===========================================
    # СТИЛИСТИЧЕСКИЕ ЭФФЕКТЫ
    # ===========================================
    
    def _effect_sepia(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Сепия фильтр"""
        def apply(frame):
            kernel = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            return np.clip(frame @ kernel.T, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_grayscale(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Черно-белый"""
        def apply(frame):
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        return video.fl_image(apply)
    
    def _effect_vintage(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Винтажный эффект"""
        def apply(frame):
            # Сепия
            kernel = np.array([[0.393, 0.769, 0.189],
                             [0.349, 0.686, 0.168],
                             [0.272, 0.534, 0.131]])
            sepia = np.clip(frame @ kernel.T, 0, 255)
            # Снижаем контраст и добавляем блеклости
            vintage = sepia * 0.85 + 30
            return np.clip(vintage, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_cinematic(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Кинематографический вид (широкоформатный)"""
        def apply(frame):
            # Темнее в тенях, контрастнее
            adjusted = frame.astype(np.float32)
            adjusted = (adjusted - 128) * 1.15 + 128
            adjusted *= 0.95
            return np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_neon(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Неоновый эффект"""
        def apply(frame):
            # Повышаем насыщенность и яркость
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= 1.6  # Насыщенность
            hsv[:, :, 2] *= 1.2  # Яркость
            hsv = np.clip(hsv, 0, 255)
            neon = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            # Добавляем свечение
            glow = cv2.GaussianBlur(neon, (21, 21), 0)
            return cv2.addWeighted(neon, 0.7, glow, 0.3, 0)
        
        return video.fl_image(apply)
    
    def _effect_retro(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Ретро эффект 80-х"""
        def apply(frame):
            # Снижаем насыщенность
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= 0.7
            retro = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            # Теплые тона
            retro = retro.astype(np.float32)
            retro[:, :, 0] *= 1.1  # Красный
            retro[:, :, 2] *= 0.9  # Синий
            return np.clip(retro, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_cyberpunk(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Киберпанк стиль"""
        def apply(frame):
            # Усиливаем синий и фиолетовый
            adjusted = frame.astype(np.float32)
            adjusted[:, :, 0] *= 1.1  # Красный
            adjusted[:, :, 1] *= 0.9  # Зеленый
            adjusted[:, :, 2] *= 1.3  # Синий
            # Повышаем контраст
            adjusted = (adjusted - 128) * 1.2 + 128
            return np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    # ===========================================
    # ФИЛЬТРЫ
    # ===========================================
    
    def _effect_blur(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Размытие"""
        strength = options.get('blur_strength', random.uniform(1.0, 3.0))
        kernel_size = int(strength * 2) * 2 + 1
        
        def apply(frame):
            return cv2.GaussianBlur(frame, (kernel_size, kernel_size), strength)
        
        return video.fl_image(apply)
    
    def _effect_sharpen(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Повышение резкости"""
        strength = options.get('sharpen_strength', random.uniform(0.5, 1.5))
        
        def apply(frame):
            kernel = np.array([[-1, -1, -1],
                             [-1, 9, -1],
                             [-1, -1, -1]]) * (strength / 3)
            return cv2.filter2D(frame, -1, kernel)
        
        return video.fl_image(apply)
    
    def _effect_edge_enhance(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Усиление краев"""
        def apply(frame):
            kernel = np.array([[0, -1, 0],
                             [-1, 5, -1],
                             [0, -1, 0]])
            return cv2.filter2D(frame, -1, kernel)
        
        return video.fl_image(apply)
    
    def _effect_emboss(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Эффект тиснения"""
        def apply(frame):
            kernel = np.array([[-2, -1, 0],
                             [-1, 1, 1],
                             [0, 1, 2]])
            embossed = cv2.filter2D(frame, -1, kernel)
            return np.clip(embossed + 128, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_noise(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Добавление шума"""
        intensity = options.get('noise_intensity', random.uniform(0.05, 0.15))
        
        def apply(frame):
            noise = np.random.normal(0, intensity * 255, frame.shape)
            return np.clip(frame + noise, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_film_grain(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Пленочное зерно"""
        intensity = options.get('grain_intensity', random.uniform(0.1, 0.25))
        
        def apply(frame):
            grain = np.random.normal(0, intensity * 255, frame.shape[:2])
            grain = np.stack([grain] * 3, axis=2)
            return np.clip(frame + grain, 0, 255).astype(np.uint8)
        
        return video.fl_image(apply)
    
    # ===========================================
    # ГЕОМЕТРИЧЕСКИЕ ЭФФЕКТЫ
    # ===========================================
    
    def _effect_vignette(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Виньетирование"""
        strength = options.get('vignette_strength', random.uniform(0.4, 0.7))
        
        def apply(frame):
            h, w = frame.shape[:2]
            X, Y = np.meshgrid(np.arange(w), np.arange(h))
            center_x, center_y = w // 2, h // 2
            max_dist = np.sqrt(center_x**2 + center_y**2)
            distance = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            vignette = 1 - (distance / max_dist) * strength
            vignette = np.clip(vignette, 0, 1)[:, :, np.newaxis]
            return (frame * vignette).astype(np.uint8)
        
        return video.fl_image(apply)
    
    def _effect_fisheye(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Эффект рыбьего глаза"""
        strength = options.get('fisheye_strength', random.uniform(0.2, 0.4))
        
        def apply(frame):
            h, w = frame.shape[:2]
            # Упрощенная версия для производительности
            center_x, center_y = w // 2, h // 2
            
            map_x = np.zeros((h, w), dtype=np.float32)
            map_y = np.zeros((h, w), dtype=np.float32)
            
            for y in range(h):
                for x in range(w):
                    dx = (x - center_x) / center_x
                    dy = (y - center_y) / center_y
                    r = np.sqrt(dx**2 + dy**2)
                    
                    if r < 1:
                        r_new = r + strength * r**3
                        factor = r_new / max(r, 0.001)
                        map_x[y, x] = center_x + dx * center_x * factor
                        map_y[y, x] = center_y + dy * center_y * factor
                    else:
                        map_x[y, x] = x
                        map_y[y, x] = y
            
            return cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)
        
        return video.fl_image(apply)
    
    def _effect_chromatic_aberration(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Хроматическая аберрация"""
        offset = options.get('aberration_offset', random.randint(2, 5))
        
        def apply(frame):
            result = frame.copy()
            # Сдвигаем красный канал
            result[:, :, 0] = np.roll(frame[:, :, 0], offset, axis=1)
            # Сдвигаем синий канал в другую сторону
            result[:, :, 2] = np.roll(frame[:, :, 2], -offset, axis=1)
            return result
        
        return video.fl_image(apply)
    
    # ===========================================
    # СПЕЦИАЛЬНЫЕ ЭФФЕКТЫ
    # ===========================================
    
    def _effect_glitch(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Глитч эффект"""
        intensity = options.get('glitch_intensity', random.uniform(0.15, 0.35))
        
        def apply(frame):
            result = frame.copy()
            h = frame.shape[0]
            
            # Случайные сдвиги по каналам
            if random.random() < intensity:
                shift = random.randint(-8, 8)
                result[:, :, 0] = np.roll(result[:, :, 0], shift, axis=1)
            
            if random.random() < intensity:
                shift = random.randint(-5, 5)
                result[:, :, 1] = np.roll(result[:, :, 1], shift, axis=0)
            
            # Случайные горизонтальные полосы
            if random.random() < intensity / 2:
                y_start = random.randint(0, h - 20)
                y_end = y_start + random.randint(3, 15)
                result[y_start:y_end, :] = np.roll(
                    result[y_start:y_end, :],
                    random.randint(-30, 30),
                    axis=1
                )
            
            return result
        
        return video.fl_image(apply)
    
    def _effect_pixelate(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Пикселизация"""
        pixel_size = options.get('pixel_size', random.randint(8, 20))
        
        def apply(frame):
            h, w = frame.shape[:2]
            # Уменьшаем
            small = cv2.resize(frame, (w // pixel_size, h // pixel_size),
                             interpolation=cv2.INTER_LINEAR)
            # Увеличиваем обратно
            return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        return video.fl_image(apply)
    
    def _effect_ascii(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """ASCII art эффект (упрощенный)"""
        levels = " .:-=+*#%@"
        
        def apply(frame):
            # Преобразуем в градации серого
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            # Уменьшаем разрешение
            small = cv2.resize(gray, (frame.shape[1] // 4, frame.shape[0] // 4))
            # Квантуем яркость
            quantized = (small / 255 * (len(levels) - 1)).astype(int)
            quantized = (quantized / (len(levels) - 1) * 255).astype(np.uint8)
            # Возвращаем в исходный размер
            result = cv2.resize(quantized, (frame.shape[1], frame.shape[0]),
                              interpolation=cv2.INTER_NEAREST)
            return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        
        return video.fl_image(apply)
    
    def _effect_mirror_horizontal(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Горизонтальное зеркало"""
        try:
            return video.fx(vfx.mirror_x)
        except:
            # Fallback: ручное зеркалирование
            return video.fl_image(lambda frame: np.fliplr(frame))
    
    def _effect_mirror_vertical(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Вертикальное зеркало"""
        try:
            return video.fx(vfx.mirror_y)
        except:
            # Fallback: ручное зеркалирование
            return video.fl_image(lambda frame: np.flipud(frame))
    
    # ===========================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ===========================================
    
    def _process_audio(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Обработка аудио"""
        if not video.audio:
            return video
        
        try:
            # Изменение громкости
            volume_factor = options.get('volume_factor', 1.0)
            if volume_factor != 1.0:
                try:
                    video = video.with_effects([afx.MultiplyVolume(volume_factor)])
                except:
                    # Fallback: ручное изменение громкости
                    audio_array = video.audio.to_soundarray()
                    audio_array = audio_array * volume_factor
                    from moviepy import AudioArrayClip
                    new_audio = AudioArrayClip(audio_array, fps=video.audio.fps)
                    video = video.with_audio(new_audio)
            
            # Изменение скорости
            speed_factor = options.get('speed_factor', 1.0)
            if speed_factor != 1.0 and 0.5 <= speed_factor <= 2.0:
                try:
                    video = video.with_effects([vfx.MultiplySpeed(speed_factor)])
                except:
                    logger.warning(f"⚠️ Изменение скорости не поддерживается в текущей версии moviepy")
            
            # Fade in/out (упрощенная версия)
            if options.get('audio_fadein', False) or options.get('audio_fadeout', False):
                try:
                    if options.get('audio_fadein', False):
                        video = video.with_effects([afx.AudioFadeIn(0.5)])
                    if options.get('audio_fadeout', False):
                        video = video.with_effects([afx.AudioFadeOut(0.5)])
                except:
                    logger.warning(f"⚠️ Audio fade эффекты не поддерживаются")
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка обработки аудио: {e}")
        
        return video
    
    def _add_text_overlay(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Добавление текста на видео"""
        try:
            text_content = options.get('text_content', '')
            if not text_content:
                return video
            
            font_size = options.get('font_size', 50)
            font_color = options.get('font_color', 'white')
            position = options.get('text_position', 'bottom')
            duration = options.get('text_duration', min(video.duration, 5))
            
            txt_clip = TextClip(
                text_content,
                fontsize=font_size,
                color=font_color,
                font='Arial-Bold',
                method='caption',
                size=(video.w - 100, None)
            ).set_duration(duration)
            
            if position == 'top':
                txt_clip = txt_clip.set_position(('center', 50))
            elif position == 'center':
                txt_clip = txt_clip.set_position('center')
            else:  # bottom
                txt_clip = txt_clip.set_position(('center', video.h - 150))
            
            return CompositeVideoClip([video, txt_clip])
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка добавления текста: {e}")
            return video
    
    def _optimize_video(self, video: VideoFileClip, options: Dict) -> VideoFileClip:
        """Оптимизация видео по размеру и качеству"""
        quality = options.get('quality', self.default_quality)
        preset = self.quality_presets.get(quality, self.quality_presets['720p'])
        target_height = preset['height']
        
        if video.h != target_height:
            aspect_ratio = video.w / video.h
            target_width = int(target_height * aspect_ratio)
            
            # Округляем до четных чисел (требование H.264)
            target_width += target_width % 2
            target_height += target_height % 2
            
            logger.info(f"📐 Изменение разрешения: {video.w}x{video.h} → {target_width}x{target_height}")
            
            try:
                # Новая версия moviepy
                video = video.resized((target_width, target_height))
            except:
                try:
                    # Старая версия moviepy
                    video = video.resize((target_width, target_height))
                except:
                    logger.warning("⚠️ Не удалось изменить разрешение")
        
        return video
    
    def _clear_file_metadata(self, file_path: Path):
        """Очистка метаданных файла"""
        try:
            temp_path = file_path.with_suffix('.temp.mp4')
            
            cmd = [
                'ffmpeg', '-i', str(file_path),
                '-map_metadata', '-1',
                '-c', 'copy',
                str(temp_path),
                '-y', '-loglevel', 'error'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                shutil.move(str(temp_path), str(file_path))
                logger.info("🔒 Метаданные очищены")
            else:
                if temp_path.exists():
                    temp_path.unlink()
                    
        except Exception as e:
            logger.warning(f"⚠️ Ошибка очистки метаданных: {e}")
    
    def _select_random_effects(self, count: int = None) -> List[str]:
        """Выбор случайных эффектов"""
        if count is None:
            count = random.randint(2, 5)
        
        # Категории эффектов для сбалансированного выбора
        color_effects = ['brightness', 'contrast', 'saturation', 'temperature']
        style_effects = ['vintage', 'cinematic', 'retro', 'neon']
        filter_effects = ['sharpen', 'film_grain', 'vignette']
        
        effects = []
        effects.extend(random.sample(color_effects, min(2, count)))
        if count > 2:
            effects.extend(random.sample(style_effects, min(1, count - 2)))
        if count > 3:
            effects.extend(random.sample(filter_effects, min(1, count - 3)))
        
        return effects[:count]
    
    def _calculate_uniqueness_score(self, effects: List[str], options: Dict) -> float:
        """Расчет индекса уникальности"""
        base_score = 0.5
        
        # Бонус за количество эффектов
        effects_bonus = min(len(effects) * 0.08, 0.3)
        
        # Бонус за сложные эффекты
        complex_effects = {'glitch', 'fisheye', 'ascii', 'chromatic_aberration', 'cyberpunk'}
        complexity_bonus = len(set(effects) & complex_effects) * 0.05
        
        # Бонус за кастомные настройки
        custom_bonus = 0.05 if options else 0
        
        total_score = base_score + effects_bonus + complexity_bonus + custom_bonus
        return min(total_score, 1.0)
    
    def _save_processing_info(self, result: ProcessingResult):
        """Сохранение информации о обработке"""
        try:
            info_file = Path(result.output_file).with_suffix('.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка сохранения информации: {e}")
    
    def get_available_effects(self) -> Dict[str, List[str]]:
        """Получение списка доступных эффектов по категориям"""
        return {
            'color': ['brightness', 'contrast', 'saturation', 'hue', 'temperature'],
            'style': ['sepia', 'grayscale', 'vintage', 'cinematic', 'neon', 'retro', 'cyberpunk'],
            'filter': ['blur', 'sharpen', 'edge_enhance', 'emboss', 'noise', 'film_grain'],
            'geometry': ['vignette', 'fisheye', 'chromatic_aberration'],
            'special': ['glitch', 'pixelate', 'ascii', 'mirror_horizontal', 'mirror_vertical']
        }
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Очистка старых файлов"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            for directory in [self.output_dir, self.temp_dir]:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age_seconds:
                            file_path.unlink()
                            deleted_count += 1
            
            logger.info(f"🧹 Очистка завершена. Удалено {deleted_count} файлов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки: {e}")


# Экспортируем для удобного использования
__all__ = ['AdvancedVideoProcessor', 'ProcessingResult']
