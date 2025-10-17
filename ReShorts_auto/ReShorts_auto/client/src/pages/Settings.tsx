import React from 'react';
import { Card } from '../components/Card';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-xl">
      <div>
        <h1 className="text-4xl font-bold text-neutral-50">Настройки</h1>
        <p className="text-neutral-400 mt-sm">Конфигурация системы</p>
      </div>

      <Card className="p-xl">
        <div className="text-center py-4xl text-neutral-400">
          <p className="text-lg">Настройки будут добавлены в следующей версии</p>
        </div>
      </Card>
    </div>
  );
};
