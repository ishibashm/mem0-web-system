'use client';

import React, { createContext, useContext, useState } from 'react';

interface DialogContextValue {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DialogContext = createContext<DialogContextValue | undefined>(undefined);

export function Dialog({
  open,
  onOpenChange,
  children,
  ...props
}: {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}) {
  const [dialogOpen, setDialogOpen] = useState(open || false);

  const handleOpenChange = (newOpen: boolean) => {
    setDialogOpen(newOpen);
    onOpenChange?.(newOpen);
  };

  return (
    <DialogContext.Provider
      value={{ open: open !== undefined ? open : dialogOpen, onOpenChange: handleOpenChange }}
    >
      <div {...props}>{children}</div>
    </DialogContext.Provider>
  );
}

export function DialogTrigger({
  children,
  ...props
}: {
  children: React.ReactNode;
}) {
  const context = useContext(DialogContext);
  if (!context) {
    throw new Error('DialogTrigger must be used within Dialog');
  }

  return (
    <button
      onClick={() => context.onOpenChange(true)}
      {...props}
    >
      {children}
    </button>
  );
}

export function DialogContent({
  children,
  ...props
}: {
  children: React.ReactNode;
}) {
  const context = useContext(DialogContext);
  if (!context) {
    throw new Error('DialogContent must be used within Dialog');
  }

  if (!context.open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md" {...props}>
        {children}
      </div>
    </div>
  );
}

export function DialogHeader({
  children,
  ...props
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="mb-4" {...props}>
      {children}
    </div>
  );
}

export function DialogTitle({
  children,
  ...props
}: {
  children: React.ReactNode;
}) {
  return (
    <h2 className="text-lg font-semibold" {...props}>
      {children}
    </h2>
  );
}

export function DialogFooter({
  children,
  ...props
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="mt-4 flex justify-end space-x-2" {...props}>
      {children}
    </div>
  );
}

export function DialogClose({
  children,
  ...props
}: {
  children: React.ReactNode;
}) {
  const context = useContext(DialogContext);
  if (!context) {
    throw new Error('DialogClose must be used within Dialog');
  }

  return (
    <button
      onClick={() => context.onOpenChange(false)}
      {...props}
    >
      {children}
    </button>
  );
}
