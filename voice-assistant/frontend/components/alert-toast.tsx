"use client";

import { toast } from "sonner";

interface ToastAlertProps {
  title: string;
  description?: string;
}

export function toastAlert({ title, description }: ToastAlertProps) {
  toast(
    <div>
      <div className="font-semibold">{title}</div>
      {description && (
        <div className="text-xs text-gray-500">{description}</div>
      )}
    </div>,
  );
}
