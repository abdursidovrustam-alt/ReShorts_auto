import React from 'react';
import { Search, Bell, User } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="h-16 bg-neutral-950 border-b border-neutral-800 fixed top-0 right-0 left-60 z-10">
      <div className="h-full px-lg flex items-center justify-between">
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-md top-1/2 -translate-y-1/2 text-neutral-400" size={20} />
            <input
              type="text"
              placeholder="Поиск..."
              className="w-full h-12 bg-background-elevated border border-neutral-600 rounded-md pl-12 pr-md text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:border-primary-500 focus:shadow-glow transition-all duration-normal"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-md ml-lg">
          <button className="relative p-2 text-neutral-400 hover:text-primary-400 hover:bg-neutral-800 rounded-lg transition-all duration-normal">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
          </button>
          
          <button className="flex items-center gap-2 p-2 text-neutral-400 hover:text-primary-400 hover:bg-neutral-800 rounded-lg transition-all duration-normal">
            <div className="w-8 h-8 bg-primary-900 rounded-full flex items-center justify-center">
              <User size={18} className="text-primary-400" />
            </div>
            <span className="font-medium">Пользователь</span>
          </button>
        </div>
      </div>
    </header>
  );
};
