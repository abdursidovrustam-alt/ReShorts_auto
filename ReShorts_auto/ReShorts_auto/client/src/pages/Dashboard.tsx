import React, { useEffect, useState } from 'react';
import { Download, Video, CheckCircle, TrendingUp } from 'lucide-react';
import { StatCard, Card } from '../components/Card';
import { getDashboardStats } from '../api/endpoints';
import { DashboardStats } from '../types';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-neutral-400">Загрузка...</div>;
  }

  return (
    <div className="space-y-2xl">
      <div>
        <h1 className="text-4xl font-bold text-neutral-50">Дашборд</h1>
        <p className="text-neutral-400 mt-sm">Обзор системы автоматизации</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-lg">
        <StatCard
          icon={<Download />}
          label="Скачано видео"
          value={stats?.stats.total_downloaded || 0}
        />
        <StatCard
          icon={<Video />}
          label="Проанализировано"
          value={stats?.stats.total_analyzed || 0}
        />
        <StatCard
          icon={<CheckCircle />}
          label="Обработано"
          value={stats?.stats.total_processed || 0}
        />
        <StatCard
          icon={<TrendingUp />}
          label="Процент успеха"
          value={`${stats?.stats.success_rate || 0}%`}
        />
      </div>

      <Card className="p-xl">
        <h2 className="text-2xl font-semibold text-neutral-100 mb-lg">Активность за 7 дней</h2>
        <div className="space-y-md">
          {stats?.activity_chart.map((day, index) => (
            <div key={index} className="flex items-center justify-between p-md bg-background-elevated rounded-md">
              <span className="text-neutral-100 font-medium">{day.date}</span>
              <div className="flex gap-lg text-sm">
                <span className="text-primary-400">Скачивания: {day.downloads}</span>
                <span className="text-success">Анализ: {day.analyzes}</span>
                <span className="text-warning">Обработка: {day.processes}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-xl">
        <h2 className="text-2xl font-semibold text-neutral-100 mb-lg">Последние операции</h2>
        <div className="space-y-md">
          {stats?.recent_operations.slice(0, 5).map((op, index) => (
            <div key={index} className="flex items-center justify-between p-md bg-background-elevated rounded-md">
              <div className="flex items-center gap-md">
                <div className={`w-2 h-2 rounded-full ${op.success ? 'bg-success' : 'bg-error'}`}></div>
                <span className="text-neutral-100 font-medium">
                  {op.type === 'download' && 'Скачивание'}
                  {op.type === 'analyze' && 'Анализ'}
                  {op.type === 'process' && 'Обработка'}
                </span>
              </div>
              <span className="text-neutral-400 text-sm">
                {new Date(op.timestamp).toLocaleString('ru-RU')}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
