#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль обработки и уникализации видео

Автор: MiniMax Agent  
Дата: 2025-10-17
"""

from .processor import AdvancedVideoProcessor, ProcessingResult
from .downloader import VideoDownloader

__version__ = '2.0.0'
__author__ = 'MiniMax Agent'

__all__ = [
    'AdvancedVideoProcessor',
    'ProcessingResult',
    'VideoDownloader'
]
