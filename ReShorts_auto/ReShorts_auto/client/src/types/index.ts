export interface Video {
  id: string;
  title: string;
  description: string;
  channel: {
    name: string;
    avatar: string;
    subscribers?: number;
  };
  thumbnail: string;
  views: number;
  likes: number;
  comments: number;
  duration: number;
  published_date: string;
  platform: 'youtube' | 'instagram' | 'tiktok' | string;
  viral_score: number;
  url: string;
  tags?: string[];
  category?: string;
  language?: string;
}

export interface FilterParams {
  platform?: string;
  query?: string;
  min_views?: number;
  max_views?: number;
  min_likes?: number;
  duration_min?: number;
  duration_max?: number;
  date_range?: string;
  language?: string;
  min_engagement?: number;
  exclude_keywords?: string[];
}

export interface FilterPreset {
  id: string;
  name: string;
  filters: FilterParams;
  created_at: string;
}

export interface DashboardStats {
  stats: {
    total_downloaded: number;
    total_analyzed: number;
    total_processed: number;
    success_rate: number;
  };
  activity_chart: ActivityChartData[];
  recent_operations: Activity[];
}

export interface ActivityChartData {
  date: string;
  downloads: number;
  analyzes: number;
  processes: number;
  total: number;
}

export interface Activity {
  timestamp: string;
  type: 'download' | 'analyze' | 'process';
  success: boolean;
}

export interface SystemStatus {
  downloaders: DownloaderStatus[];
  ai_providers: AIProviderStatus[];
  timestamp: string;
}

export interface DownloaderStatus {
  name: string;
  available: boolean;
  platforms: string[];
  priority: number;
}

export interface AIProviderStatus {
  name: string;
  available: boolean;
  priority: number;
}

export interface Config {
  search: {
    queries: string[];
    max_results: number;
    date_range: string;
    min_views: number;
    min_engagement: number;
  };
  ai: {
    providers: Record<string, any>;
    timeout: number;
    max_retries: number;
    cache_enabled: boolean;
  };
  download: {
    methods: Record<string, any>;
    video_quality: string;
    max_file_size: number;
    path: string;
    subtitles: boolean;
    thumbnail: boolean;
    proxy: {
      enabled: boolean;
      url: string;
    };
  };
  processing: {
    clip_duration: number;
    clips_per_video: number;
    output_format: string;
    video_bitrate: number;
    auto_crop: boolean;
    add_watermark: boolean;
    filter_duplicates: boolean;
    filter_low_quality: boolean;
    exclude_keywords: string[];
  };
  scenarios: {
    auto_search: boolean;
    auto_download: boolean;
    auto_analyze: boolean;
    auto_process: boolean;
    auto_run_interval: number;
    notify_on_complete: boolean;
    notify_on_error: boolean;
  };
}
