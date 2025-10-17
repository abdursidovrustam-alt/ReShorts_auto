import React, { useEffect, useState } from 'react';
import { Card } from '../components/Card';
import { getSystemStatus } from '../api/endpoints';
import { SystemStatus } from '../types';

export const Status: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await getSystemStatus();
      setStatus(data);
    } catch (error) {
      console.error('Error loading status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-neutral-400">Загрузка...</div>;
  }

  return (
    <div className="space-y-xl">
      <div>
        <h1 className="text-4xl font-bold text-neutral-50">Статус системы</h1>
        <p className="text-neutral-400 mt-sm">Состояние загрузчиков и AI провайдеров</p>
      </div>

      <Card className="p-xl">
        <h2 className="text-2xl font-semibold text-neutral-100 mb-lg">Загрузчики</h2>
        <div className="space-y-md">
          {status?.downloaders.map((downloader) => (
            <div key={downloader.name} className="flex items-center justify-between p-md bg-background-elevated rounded-md">
              <div>
                <span className="text-neutral-100 font-medium">{downloader.name}</span>
                <p className="text-neutral-400 text-sm">{downloader.platforms.join(', ')}</p>
              </div>
              <div className={`px-md py-1 rounded-full text-sm ${
                downloader.available
                  ? 'bg-success/20 text-success'
                  : 'bg-error/20 text-error'
              }`}>
                {downloader.available ? 'Доступен' : 'Недоступен'}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-xl">
        <h2 className="text-2xl font-semibold text-neutral-100 mb-lg">AI Провайдеры</h2>
        <div className="space-y-md">
          {status?.ai_providers.map((provider) => (
            <div key={provider.name} className="flex items-center justify-between p-md bg-background-elevated rounded-md">
              <span className="text-neutral-100 font-medium">{provider.name}</span>
              <div className={`px-md py-1 rounded-full text-sm ${
                provider.available
                  ? 'bg-success/20 text-success'
                  : 'bg-error/20 text-error'
              }`}>
                {provider.available ? 'Доступен' : 'Недоступен'}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
