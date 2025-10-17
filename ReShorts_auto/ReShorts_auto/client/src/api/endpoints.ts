import api from './axios';
import { 
  Video, 
  FilterParams, 
  FilterPreset, 
  DashboardStats, 
  SystemStatus,
  Config 
} from '../types';

// Поиск и предпросмотр
export const searchVideos = async (params: FilterParams) => {
  const response = await api.post<{ success: boolean; total: number; videos: Video[] }>('/search/preview', params);
  return response.data;
};

export const getVideoDetails = async (videoId: string) => {
  const response = await api.get<Video>(`/video/details/${videoId}`);
  return response.data;
};

// Скачивание
export const downloadVideo = async (url: string, platform?: string) => {
  const response = await api.post('/download', { url, platform });
  return response.data;
};

export const downloadBatch = async (urls: string[]) => {
  const response = await api.post('/download/batch', { urls });
  return response.data;
};

// Анализ
export const analyzeVideo = async (videoData: any, prompt?: string) => {
  const response = await api.post('/analyze', { video_data: videoData, prompt });
  return response.data;
};

// Фильтры пресеты
export const saveFilterPreset = async (name: string, filters: FilterParams) => {
  const response = await api.post<{ success: boolean; preset: FilterPreset }>('/filters/save', { name, filters });
  return response.data;
};

export const getFilterPresets = async () => {
  const response = await api.get<{ success: boolean; presets: FilterPreset[] }>('/filters/list');
  return response.data;
};

export const deleteFilterPreset = async (presetId: string) => {
  const response = await api.delete(`/filters/delete/${presetId}`);
  return response.data;
};

// Статистика
export const getDashboardStats = async () => {
  const response = await api.get<DashboardStats>('/stats/dashboard');
  return response.data;
};

// Система
export const getSystemStatus = async () => {
  const response = await api.get<SystemStatus>('/status');
  return response.data;
};

// Файлы
export const getFilesList = async () => {
  const response = await api.get<{ files: any[] }>('/files/list');
  return response.data;
};

export const deleteFile = async (filename: string) => {
  const response = await api.delete(`/files/delete/${filename}`);
  return response.data;
};

// Конфигурация
export const getConfig = async () => {
  const response = await api.get<Config>('/config/get');
  return response.data;
};

export const saveConfig = async (config: Config) => {
  const response = await api.post('/config/save', config);
  return response.data;
};
