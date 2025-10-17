#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Processor - Модуль обработки и уникализации видео
15+ фильтров и эффектов для создания уникального контента
"""

import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
from moviepy.editor import TextClip, ColorClip, concatenate_videoclips
from moviepy.config import FFMPEG_BINARY
from pathlib import Path
import random
import time
from datetime import datetime
from loguru import logger
import json
from PIL import Image, ImageFilter, ImageEnhance
import subprocess
import tempfile
import shutil

class VideoProcessor:
    """Класс для обработки и уникализации видео"""
    
    def __init__(self, config):
        self.config = config
        self.processed_dir = Path(config.get('paths', {}).get('processed', './processed'))
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройки обработки
        self.output_quality = config.get('video_processing', {}).get('output_quality', '720p')
        self.max_duration = config.get('video_processing', {}).get('max_duration', 60)
        self.clear_metadata = config.get('video_processing', {}).get('clear_metadata', True)
        
        # Доступные фильтры
        self.available_filters = {
            'blur': self._apply_blur,
            'sharpen': self._apply_sharpen,
            'brightness': self._apply_brightness,
            'contrast': self._apply_contrast,
            'saturation': self._apply_saturation,
            'sepia': self._apply_sepia,
            'grayscale': self._apply_grayscale,
            'vintage': self._apply_vintage,
            'film_grain': self._apply_film_grain,
            'vignette': self._apply_vignette,
            'fisheye': self._apply_fisheye,
            'mirror': self._apply_mirror,
            'emboss': self._apply_emboss,
            'edge_enhance': self._apply_edge_enhance,
            'retro': self._apply_retro,
            'neon': self._apply_neon,
            'glitch': self._apply_glitch
        }
        
        # Настройки качества
        self.quality_settings = {
            '480p': {'height': 480, 'bitrate': '1000k'},
            '720p': {'height': 720, 'bitrate': '2500k'},
            '1080p': {'height': 1080, 'bitrate': '5000k'}
        }
    
    def process_video(self, input_file, options=None):
        """Основной метод обработки видео"""
        if not input_file or not Path(input_file).exists():
            logger.error(f"Входной файл не найден: {input_file}")
            return None
        
        options = options or {}
        input_path = Path(input_file)
        
        logger.info(f"Начало обработки видео: {input_path.name}")
        
        try:
            # Генерируем уникальное имя выходного файла
            timestamp = int(time.time())
            output_filename = f"processed_{input_path.stem}_{timestamp}.mp4"
            output_path = self.processed_dir / output_filename
            
            # Загружаем видео
            with VideoFileClip(str(input_file)) as video:
                # Проверяем и обрезаем длительность
                if video.duration > self.max_duration:
                    logger.info(f"Обрезаем видео с {video.duration:.1f}с до {self.max_duration}с")
                    video = video.subclip(0, self.max_duration)
                
                # Применяем видео фильтры
                processed_video = self._apply_video_effects(video, options)
                
                # Обрабатываем аудио
                processed_video = self._process_audio(processed_video, options)
                
                # Добавляем текст и эффекты
                processed_video = self._add_text_effects(processed_video, options)
                
                # Оптимизируем размер и качество
                processed_video = self._optimize_video(processed_video)
                
                # Сохраняем результат
                quality_settings = self.quality_settings.get(self.output_quality, self.quality_settings['720p'])
                
                logger.info(f"Сохранение обработанного видео: {output_path}")
                
                processed_video.write_videofile(
                    str(output_path),
                    codec='libx264',
                    audio_codec='aac',
                    bitrate=quality_settings['bitrate'],
                    verbose=False,
                    logger=None
                )
            
            # Очистка метаданных
            if self.clear_metadata:
                self._clear_metadata(output_path)
            
            # Сохраняем информацию о обработке
            self._save_processing_info(input_file, output_path, options)
            
            logger.info(f"Обработка завершена: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Ошибка обработки видео: {e}")
            return None
    
    def _apply_video_effects(self, video, options):
        """Применение видео эффектов"""
        filters = options.get('filters', [])
        
        if not filters:
            # Применяем случайные легкие фильтры по умолчанию
            filters = random.choices(['brightness', 'contrast', 'saturation'], k=random.randint(1, 2))
            logger.info(f"Применяем случайные фильтры: {filters}")
        
        processed_video = video
        
        for filter_name in filters:
            if filter_name in self.available_filters:
                try:
                    logger.info(f"Применяем фильтр: {filter_name}")
                    filter_func = self.available_filters[filter_name]
                    processed_video = filter_func(processed_video, options)
                except Exception as e:
                    logger.warning(f"Ошибка применения фильтра {filter_name}: {e}")
                    continue
            else:
                logger.warning(f"Неизвестный фильтр: {filter_name}")
        
        return processed_video
    
    def _apply_blur(self, video, options):
        """Применение размытия"""
        strength = options.get('blur_strength', random.uniform(0.5, 2.0))
        
        def blur_frame(frame):
            return cv2.GaussianBlur(frame, (int(strength*4)+1, int(strength*4)+1), strength)
        
        return video.fl_image(blur_frame)
    
    def _apply_sharpen(self, video, options):
        """Применение резкости"""
        strength = options.get('sharpen_strength', random.uniform(0.3, 1.0))
        
        def sharpen_frame(frame):
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) * strength
            return cv2.filter2D(frame, -1, kernel)
        
        return video.fl_image(sharpen_frame)
    
    def _apply_brightness(self, video, options):
        """Изменение яркости"""
        factor = options.get('brightness_factor', random.uniform(0.8, 1.2))
        
        def adjust_brightness(frame):
            return np.clip(frame * factor, 0, 255).astype(np.uint8)
        
        return video.fl_image(adjust_brightness)
    
    def _apply_contrast(self, video, options):
        """Изменение контрастности"""
        factor = options.get('contrast_factor', random.uniform(0.9, 1.3))
        
        def adjust_contrast(frame):
            mean = np.mean(frame)
            return np.clip((frame - mean) * factor + mean, 0, 255).astype(np.uint8)
        
        return video.fl_image(adjust_contrast)
    
    def _apply_saturation(self, video, options):
        """Изменение насыщенности"""
        factor = options.get('saturation_factor', random.uniform(0.8, 1.4))
        
        def adjust_saturation(frame):
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= factor
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        return video.fl_image(adjust_saturation)
    
    def _apply_sepia(self, video, options):
        """Применение сепии"""
        def sepia_filter(frame):
            sepia_kernel = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            return np.clip(frame @ sepia_kernel.T, 0, 255).astype(np.uint8)
        
        return video.fl_image(sepia_filter)
    
    def _apply_grayscale(self, video, options):
        """Преобразование в черно-белое"""
        def grayscale_filter(frame):
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        
        return video.fl_image(grayscale_filter)
    
    def _apply_vintage(self, video, options):
        """Винтажный эффект"""
        def vintage_filter(frame):
            # Комбинация сепии и снижения контраста
            sepia_kernel = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            sepia_frame = np.clip(frame @ sepia_kernel.T, 0, 255)
            # Снижаем контраст
            vintage_frame = sepia_frame * 0.8 + 40
            return np.clip(vintage_frame, 0, 255).astype(np.uint8)
        
        return video.fl_image(vintage_filter)
    
    def _apply_film_grain(self, video, options):
        """Добавление пленочного зерна"""
        intensity = options.get('grain_intensity', random.uniform(0.1, 0.3))
        
        def add_grain(frame):
            noise = np.random.normal(0, intensity * 255, frame.shape)
            noisy_frame = frame + noise
            return np.clip(noisy_frame, 0, 255).astype(np.uint8)
        
        return video.fl_image(add_grain)
    
    def _apply_vignette(self, video, options):
        """Добавление виньетирования"""
        strength = options.get('vignette_strength', random.uniform(0.3, 0.7))
        
        def apply_vignette(frame):
            h, w = frame.shape[:2]
            X, Y = np.meshgrid(np.arange(w), np.arange(h))
            center_x, center_y = w // 2, h // 2
            max_distance = np.sqrt(center_x**2 + center_y**2)
            distance = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            vignette = 1 - (distance / max_distance) * strength
            vignette = np.clip(vignette, 0, 1)
            
            if len(frame.shape) == 3:
                vignette = vignette[:, :, np.newaxis]
            
            return (frame * vignette).astype(np.uint8)
        
        return video.fl_image(apply_vignette)
    
    def _apply_fisheye(self, video, options):
        """Эффект рыбьего глаза"""
        strength = options.get('fisheye_strength', random.uniform(0.2, 0.5))
        
        def fisheye_effect(frame):
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            
            # Создаем карту дисторсии
            map_x = np.zeros((h, w), dtype=np.float32)
            map_y = np.zeros((h, w), dtype=np.float32)
            
            for y in range(h):
                for x in range(w):
                    dx = x - center_x
                    dy = y - center_y
                    distance = np.sqrt(dx**2 + dy**2)
                    max_distance = min(center_x, center_y)
                    
                    if distance <= max_distance:
                        normalized_distance = distance / max_distance
                        distorted_distance = normalized_distance * (1 + strength * normalized_distance**2)
                        
                        if distance > 0:
                            factor = distorted_distance / normalized_distance
                            map_x[y, x] = center_x + dx * factor
                            map_y[y, x] = center_y + dy * factor
                        else:
                            map_x[y, x] = x
                            map_y[y, x] = y
                    else:
                        map_x[y, x] = x
                        map_y[y, x] = y
            
            return cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR)
        
        return video.fl_image(fisheye_effect)
    
    def _apply_mirror(self, video, options):
        """Зеркальный эффект"""
        mode = options.get('mirror_mode', random.choice(['horizontal', 'vertical']))
        
        def mirror_effect(frame):
            if mode == 'horizontal':
                return np.hstack([frame, np.fliplr(frame)])
            else:  # vertical
                return np.vstack([frame, np.flipud(frame)])
        
        return video.fl_image(mirror_effect)
    
    def _apply_emboss(self, video, options):
        """Эффект тиснения"""
        def emboss_effect(frame):
            kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
            embossed = cv2.filter2D(frame, -1, kernel)
            return np.clip(embossed + 128, 0, 255).astype(np.uint8)
        
        return video.fl_image(emboss_effect)
    
    def _apply_edge_enhance(self, video, options):
        """Усиление краев"""
        def edge_enhance(frame):
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            return cv2.filter2D(frame, -1, kernel)
        
        return video.fl_image(edge_enhance)
    
    def _apply_retro(self, video, options):
        """Ретро эффект"""
        def retro_effect(frame):
            # Комбинация нескольких эффектов
            # 1. Снижаем насыщенность
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= 0.7
            frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # 2. Добавляем теплые тона
            frame[:, :, 0] = np.clip(frame[:, :, 0] * 1.1, 0, 255)  # красный
            frame[:, :, 1] = np.clip(frame[:, :, 1] * 1.05, 0, 255)  # зеленый
            frame[:, :, 2] = np.clip(frame[:, :, 2] * 0.9, 0, 255)  # синий
            
            return frame.astype(np.uint8)
        
        return video.fl_image(retro_effect)
    
    def _apply_neon(self, video, options):
        """Неоновый эффект"""
        def neon_effect(frame):
            # Повышаем контраст и насыщенность
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= 1.5  # насыщенность
            hsv[:, :, 2] *= 1.2  # яркость
            hsv = np.clip(hsv, 0, 255)
            frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # Добавляем свечение
            glow = cv2.GaussianBlur(frame, (21, 21), 0)
            neon_frame = cv2.addWeighted(frame, 0.7, glow, 0.3, 0)
            
            return neon_frame
        
        return video.fl_image(neon_effect)
    
    def _apply_glitch(self, video, options):
        """Глитч эффект"""
        intensity = options.get('glitch_intensity', random.uniform(0.1, 0.3))
        
        def glitch_effect(frame):
            h, w = frame.shape[:2]
            
            # Случайные сдвиги по каналам
            if random.random() < intensity:
                # Сдвиг красного канала
                shift = random.randint(-5, 5)
                frame[:, :, 0] = np.roll(frame[:, :, 0], shift, axis=1)
            
            if random.random() < intensity:
                # Сдвиг зеленого канала
                shift = random.randint(-3, 3)
                frame[:, :, 1] = np.roll(frame[:, :, 1], shift, axis=0)
            
            # Случайные полосы
            if random.random() < intensity / 2:
                y_start = random.randint(0, h - 10)
                y_end = y_start + random.randint(1, 10)
                frame[y_start:y_end, :] = np.roll(frame[y_start:y_end, :], random.randint(-20, 20), axis=1)
            
            return frame
        
        return video.fl_image(glitch_effect)
    
    def _process_audio(self, video, options):
        """Обработка аудио"""
        if not video.audio:
            return video
        
        audio_options = options.get('audio', {})
        
        # Изменение скорости воспроизведения
        speed_factor = audio_options.get('speed_factor', 1.0)
        if speed_factor != 1.0:
            logger.info(f"Изменение скорости аудио: {speed_factor}x")
            new_audio = video.audio.fx.speedx(speed_factor)
            video = video.set_audio(new_audio)
        
        # Изменение громкости
        volume_factor = audio_options.get('volume_factor', 1.0)
        if volume_factor != 1.0:
            logger.info(f"Изменение громкости: {volume_factor}x")
            new_audio = video.audio.fx.volumex(volume_factor)
            video = video.set_audio(new_audio)
        
        return video
    
    def _add_text_effects(self, video, options):
        """Добавление текстовых эффектов"""
        text_options = options.get('text', {})
        
        if not text_options.get('enabled', False):
            return video
        
        try:
            text_content = text_options.get('content', 'Обработано AI')
            font_size = text_options.get('font_size', 40)
            font_color = text_options.get('font_color', 'white')
            position = text_options.get('position', 'bottom')
            duration = text_options.get('duration', min(video.duration, 3))
            
            # Создаем текстовый клип
            txt_clip = TextClip(
                text_content,
                fontsize=font_size,
                color=font_color,
                font='Arial-Bold'
            ).set_duration(duration)
            
            # Определяем позицию
            if position == 'top':
                txt_clip = txt_clip.set_position(('center', 50))
            elif position == 'center':
                txt_clip = txt_clip.set_position('center')
            else:  # bottom
                txt_clip = txt_clip.set_position(('center', video.h - 100))
            
            # Компонуем с видео
            video = CompositeVideoClip([video, txt_clip])
            logger.info(f"Добавлен текст: '{text_content}'")
            
        except Exception as e:
            logger.warning(f"Ошибка добавления текста: {e}")
        
        return video
    
    def _optimize_video(self, video):
        """Оптимизация видео по размеру и качеству"""
        quality_settings = self.quality_settings.get(self.output_quality, self.quality_settings['720p'])
        target_height = quality_settings['height']
        
        # Изменяем размер если необходимо
        if video.h != target_height:
            aspect_ratio = video.w / video.h
            target_width = int(target_height * aspect_ratio)
            
            # Округляем до четных чисел (требование H.264)
            target_width = target_width + (target_width % 2)
            target_height = target_height + (target_height % 2)
            
            logger.info(f"Изменение разрешения: {video.w}x{video.h} -> {target_width}x{target_height}")
            video = video.resize((target_width, target_height))
        
        return video
    
    def _clear_metadata(self, video_path):
        """Очистка метаданных"""
        try:
            temp_path = str(video_path) + ".temp.mp4"
            
            # Команда ffmpeg для очистки метаданных
            cmd = [
                'ffmpeg', '-i', str(video_path),
                '-map_metadata', '-1',  # Удаляем все метаданные
                '-c', 'copy',  # Копируем без перекодирования
                temp_path,
                '-y'  # Перезаписать если существует
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Заменяем оригинальный файл
                shutil.move(temp_path, video_path)
                logger.info("Метаданные очищены")
            else:
                logger.warning(f"Ошибка очистки метаданных: {result.stderr}")
                if Path(temp_path).exists():
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.warning(f"Ошибка очистки метаданных: {e}")
    
    def _save_processing_info(self, input_file, output_file, options):
        """Сохранение информации о обработке"""
        try:
            info = {
                'input_file': str(input_file),
                'output_file': str(output_file),
                'processing_options': options,
                'timestamp': datetime.now().isoformat(),
                'output_quality': self.output_quality,
                'filters_applied': options.get('filters', []),
                'file_size_mb': round(Path(output_file).stat().st_size / (1024*1024), 2)
            }
            
            info_file = Path(output_file).with_suffix('.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Информация о обработке сохранена: {info_file}")
            
        except Exception as e:
            logger.warning(f"Ошибка сохранения информации: {e}")
    
    def get_available_filters(self):
        """Получение списка доступных фильтров"""
        return {
            'filters': list(self.available_filters.keys()),
            'descriptions': {
                'blur': 'Размытие',
                'sharpen': 'Повышение резкости',
                'brightness': 'Яркость',
                'contrast': 'Контрастность',
                'saturation': 'Насыщенность',
                'sepia': 'Сепия',
                'grayscale': 'Черно-белое',
                'vintage': 'Винтаж',
                'film_grain': 'Пленочное зерно',
                'vignette': 'Виньетирование',
                'fisheye': 'Рыбий глаз',
                'mirror': 'Зеркало',
                'emboss': 'Тиснение',
                'edge_enhance': 'Усиление краев',
                'retro': 'Ретро',
                'neon': 'Неон',
                'glitch': 'Глитч'
            }
        }
    
    def batch_process(self, input_files, options=None, progress_callback=None):
        """Пакетная обработка видео"""
        results = []
        total = len(input_files)
        
        logger.info(f"Начало пакетной обработки {total} видео")
        
        for i, input_file in enumerate(input_files):
            try:
                if progress_callback:
                    progress_callback(i, total, f"Обработка {i+1}/{total}")
                
                output_file = self.process_video(input_file, options)
                
                results.append({
                    'input_file': input_file,
                    'output_file': output_file,
                    'success': output_file is not None,
                    'error': None if output_file else 'Ошибка обработки'
                })
                
            except Exception as e:
                logger.error(f"Ошибка пакетной обработки {input_file}: {e}")
                results.append({
                    'input_file': input_file,
                    'output_file': None,
                    'success': False,
                    'error': str(e)
                })
        
        successful = len([r for r in results if r['success']])
        logger.info(f"Пакетная обработка завершена. Успешно: {successful}/{total}")
        
        return results
    
    def clean_old_files(self, max_age_hours=24):
        """Очистка старых обработанных файлов"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            deleted_count = 0
            
            for file_path in self.processed_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Удален старый файл: {file_path.name}")
            
            logger.info(f"Очистка завершена. Удалено {deleted_count} файлов")
            
        except Exception as e:
            logger.error(f"Ошибка очистки: {e}")