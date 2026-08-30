"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface StatusChipProps {
  status: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig: Record<string, { variant: string; className: string }> = {
  completed: { variant: 'success', className: 'bg-green-500/10 text-green-500 border-green-500/20' },
  running: { variant: 'info', className: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
  scheduled: { variant: 'default', className: 'bg-gray-500/10 text-gray-500 border-gray-500/20' },
  failed: { variant: 'error', className: 'bg-red-500/10 text-red-500 border-red-500/20' },
  active: { variant: 'success', className: 'bg-green-500/10 text-green-500 border-green-500/20' },
  inactive: { variant: 'default', className: 'bg-gray-500/10 text-gray-500 border-gray-500/20' },
  open: { variant: 'success', className: 'bg-green-500/10 text-green-500 border-green-500/20' },
  closed: { variant: 'default', className: 'bg-gray-500/10 text-gray-500 border-gray-500/20' },
  enabled: { variant: 'success', className: 'bg-green-500/10 text-green-500 border-green-500/20' },
  disabled: { variant: 'default', className: 'bg-gray-500/10 text-gray-500 border-gray-500/20' },
  hire: { variant: 'success', className: 'bg-green-500/10 text-green-500 border-green-500/20' },
  maybe: { variant: 'warning', className: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' },
  reject: { variant: 'error', className: 'bg-red-500/10 text-red-500 border-red-500/20' },
};

export function StatusChip({ status, variant, size = 'md' }: StatusChipProps) {
  // Handle undefined/null status
  if (!status || typeof status !== 'string') {
    return (
      <Badge
        variant="outline"
        className={cn(
          "font-medium border",
          "bg-gray-500/10 text-gray-500 border-gray-500/20",
          size === 'sm' && "text-xs px-2 py-0.5",
          size === 'md' && "text-xs px-2.5 py-1",
          size === 'lg' && "text-sm px-3 py-1.5"
        )}
      >
        Unknown
      </Badge>
    );
  }

  const config = statusConfig[status.toLowerCase()] || { 
    variant: 'default', 
    className: 'bg-gray-500/10 text-gray-500 border-gray-500/20' 
  };

  return (
    <Badge
      variant="outline"
      className={cn(
        "font-medium border capitalize",
        config.className,
        size === 'sm' && "text-xs px-2 py-0.5",
        size === 'md' && "text-xs px-2.5 py-1",
        size === 'lg' && "text-sm px-3 py-1.5"
      )}
    >
      {status}
    </Badge>
  );
}

