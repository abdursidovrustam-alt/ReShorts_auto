import React from 'react';
import { Card } from '../components/Card';

export const VideoManager: React.FC = () => {
  return (
    <div className="space-y-xl">
      <div>
        <h1 className="text-4xl font-bold text-neutral-50">Управление видео</h1>
        <p className="text-neutral-400 mt-sm">Скачанные и обработанные видео</p>
      </div>

      <Card className="p-xl">
        <div className="text-center py-4xl text-neutral-400">
          <p className="text-lg">Здесь будет отображаться список скачанных видео</p>
        </div>
      </Card>
    </div>
  );
};
