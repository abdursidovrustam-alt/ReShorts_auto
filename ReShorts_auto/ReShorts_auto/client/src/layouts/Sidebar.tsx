import React from 'react';
import { NavLink } from 'react-router-dom';
import { Home, Search, Video, Settings, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigationItems = [
  { name: 'Дашборд', path: '/', icon: Home },
  { name: 'Поиск', path: '/search', icon: Search },
  { name: 'Видео', path: '/videos', icon: Video },
  { name: 'Настройки', path: '/settings', icon: Settings },
  { name: 'Статус', path: '/status', icon: Activity },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-60 bg-neutral-950 border-r border-neutral-800 h-screen fixed left-0 top-0 flex flex-col">
      <div className="p-lg border-b border-neutral-800">
        <h1 className="text-2xl font-bold text-primary-500">ReShorts</h1>
        <p className="text-sm text-neutral-400 mt-1">Автоматизация</p>
      </div>
      
      <nav className="flex-1 p-md">
        <ul className="space-y-2">
          {navigationItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-md py-3 rounded-lg transition-all duration-normal',
                    'text-neutral-400 hover:text-primary-400 hover:bg-neutral-800',
                    isActive && 'bg-primary-900 text-primary-400 border border-primary-500 shadow-glow'
                  )
                }
              >
                <item.icon size={20} />
                <span className="font-medium">{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      <div className="p-lg border-t border-neutral-800">
        <div className="text-xs text-neutral-500">
          <p>Версия 1.0.0</p>
          <p className="mt-1">Автор: MiniMax Agent</p>
        </div>
      </div>
    </aside>
  );
};
