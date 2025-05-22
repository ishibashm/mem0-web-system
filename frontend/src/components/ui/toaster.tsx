'use client';

import React from 'react';

export interface ToastProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
}

export const Toaster = () => {
  return <div id="toaster" className="fixed top-0 right-0 z-50 p-4"></div>;
};

export const useToast = () => {
  const toast = (props: ToastProps) => {
    console.log('Toast:', props);
  };
  
  return { toast };
};
