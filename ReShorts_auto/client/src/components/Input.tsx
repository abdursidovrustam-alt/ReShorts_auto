import React from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, icon, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-neutral-400 mb-sm">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-md top-1/2 -translate-y-1/2 text-neutral-400">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'w-full h-12 bg-background-elevated border border-neutral-600 rounded-md',
              'px-md text-base text-neutral-100 placeholder:text-neutral-500',
              'transition-all duration-normal',
              'focus:outline-none focus:border-primary-500 focus:shadow-glow',
              'disabled:opacity-60 disabled:cursor-not-allowed',
              icon && 'pl-12',
              error && 'border-error focus:border-error',
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-sm text-sm text-error">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
