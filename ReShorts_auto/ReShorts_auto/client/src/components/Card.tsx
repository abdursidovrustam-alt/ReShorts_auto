import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className, hover = false, onClick }) => {
  const baseStyles = 'bg-background-surface rounded-lg shadow-md transition-all duration-smooth';
  const hoverStyles = hover ? 'hover:-translate-y-1 hover:shadow-lg hover:shadow-glow hover:scale-[1.02] cursor-pointer' : '';
  
  return (
    <div className={cn(baseStyles, hoverStyles, className)} onClick={onClick}>
      {children}
    </div>
  );
};

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  change?: {
    value: string;
    type: 'increase' | 'decrease';
  };
}

export const StatCard: React.FC<StatCardProps> = ({ icon, label, value, change }) => {
  return (
    <Card className="p-xl">
      <div className="flex items-center gap-md mb-sm">
        <div className="text-primary-500 text-2xl">{icon}</div>
        <p className="text-neutral-400 text-sm uppercase tracking-wider">{label}</p>
      </div>
      <div className="text-5xl font-bold text-neutral-50 mb-sm">{value}</div>
      {change && (
        <div className={cn(
          'flex items-center gap-1 text-sm',
          change.type === 'increase' ? 'text-success' : 'text-error'
        )}>
          <span>{change.type === 'increase' ? '↑' : '↓'}</span>
          <span>{change.value}</span>
        </div>
      )}
    </Card>
  );
};
