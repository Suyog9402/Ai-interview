import { AppConfig } from "./types";

export function getAppConfig(headers: HeadersInit): AppConfig {
  // Example: parse headers or environment for config
  // For now, just return defaults (can be extended)
  return {
    companyName: "LiveKit",
    pageDescription: "A voice agent built with LiveKit",
    supportsChatInput: true,
    supportsVideoInput: true,
    supportsScreenShare: true,
    isPreConnectBufferEnabled: true,
    logo: "/lk-logo.svg",
    accent: "#002cf2",
    logoDark: "/lk-logo-dark.svg",
    accentDark: "#1fd5f9",
    startButtonText: "Start call",
  };
}

// Utility for merging class names (copied from clsx/tailwind-merge pattern)
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export const THEME_STORAGE_KEY = "theme-mode";
export const THEME_MEDIA_QUERY = "(prefers-color-scheme: dark)";

export function cn(...inputs: any[]) {
  return twMerge(clsx(inputs));
}
