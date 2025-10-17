import React, { useState } from 'react';
import { Search as SearchIcon, Filter } from 'lucide-react';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import { searchVideos } from '../api/endpoints';
import { Video, FilterParams } from '../types';

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [platform, setPlatform] = useState('all');
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params: FilterParams = {
        query,
        platform: platform === 'all' ? undefined : platform,
      };
      const result = await searchVideos(params);
      setVideos(result.videos);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-xl">
      <div>
        <h1 className="text-4xl font-bold text-neutral-50">Поиск видео</h1>
        <p className="text-neutral-400 mt-sm">Найдите вирусные видео с фильтрами</p>
      </div>

      <Card className="p-xl">
        <div className="space-y-lg">
          <div className="flex gap-md">
            <div className="flex-1">
              <Input
                placeholder="Введите ключевые слова..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                icon={<SearchIcon size={20} />}
              />
            </div>
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? 'Загрузка...' : 'Искать'}
            </Button>
          </div>

          <div className="flex gap-md items-center">
            <span className="text-neutral-400">Платформа:</span>
            {['all', 'youtube', 'instagram', 'tiktok'].map((p) => (
              <button
                key={p}
                onClick={() => setPlatform(p)}
                className={`px-md py-2 rounded-full text-sm transition-all duration-normal ${
                  platform === p
                    ? 'bg-primary-900 border border-primary-500 text-primary-400'
                    : 'bg-neutral-700 text-neutral-400 hover:bg-neutral-600'
                }`}
              >
                {p === 'all' ? 'Все' : p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {videos.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-xl">
          {videos.map((video) => (
            <Card key={video.id} hover className="overflow-hidden">
              <img src={video.thumbnail} alt={video.title} className="w-full aspect-video object-cover" />
              <div className="p-lg space-y-md">
                <h3 className="text-xl font-semibold text-neutral-100 line-clamp-2">{video.title}</h3>
                <div className="flex items-center gap-md">
                  <img src={video.channel.avatar} alt={video.channel.name} className="w-8 h-8 rounded-full" />
                  <span className="text-neutral-400 text-sm">{video.channel.name}</span>
                </div>
                <div className="flex items-center gap-lg text-neutral-400 text-sm">
                  <span>{video.views.toLocaleString()} просм.</span>
                  <span>{video.likes.toLocaleString()} лайков</span>
                </div>
                <div className="flex gap-sm">
                  <Button size="sm" className="flex-1">Скачать</Button>
                  <Button size="sm" variant="secondary">Подробнее</Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
