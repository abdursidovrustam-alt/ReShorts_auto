import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-normal focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-background-base disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variantStyles = {
      primary: 'bg-primary-500 text-neutral-950 hover:bg-primary-600 hover:shadow-glow active:bg-primary-700 active:scale-95',
      secondary: 'bg-transparent border border-neutral-700 text-neutral-100 hover:border-primary-500 hover:text-primary-400 hover:shadow-glow',
      ghost: 'bg-transparent text-neutral-100 hover:bg-neutral-700 hover:text-primary-400',
    };
    
    const sizeStyles = {
      sm: 'px-3 py-2 text-sm h-9',
      md: 'px-6 py-3 text-base h-12',
      lg: 'px-8 py-4 text-lg h-14',
    };
    
    return (
      <button
        ref={ref}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
