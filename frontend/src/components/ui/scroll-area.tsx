'use client';

import React from 'react';

export interface ScrollAreaProps {
  className?: string;
  children: React.ReactNode;
}

export function ScrollArea({ className, children, ...props }: ScrollAreaProps) {
  return (
    <div 
      className={`overflow-auto ${className || ''}`} 
      {...props}
    >
      {children}
    </div>
  );
}
