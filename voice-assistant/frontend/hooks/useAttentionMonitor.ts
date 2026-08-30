import { useEffect, useRef, useState } from "react";

type Options = {
  // mark suspicious if hidden this long (ms)
  longHideMs?: number; // default 5000
  // mark suspicious if switches exceed this within window (N per windowMs)
  maxSwitchesPerWindow?: number; // default 3
  windowMs?: number; // default 30000
  onSuspicious?: (reason: string, data?: Record<string, any>) => void;
};

export function useAttentionMonitor(opts: Options = {}) {
  const {
    longHideMs = 5000,
    maxSwitchesPerWindow = 3,
    windowMs = 30000,
    onSuspicious,
  } = opts;

  const [isTabHidden, setIsTabHidden] = useState(false);
  const [lastHiddenDurationMs, setLastHiddenDurationMs] = useState(0);

  const hideStartedAt = useRef<number | null>(null);
  const switches = useRef<number[]>([]); // timestamps of visibility changes
  const focused = useRef<boolean>(true);

  useEffect(() => {
    if (typeof document === "undefined") return;

    const onVis = () => {
      const hidden = document.visibilityState === "hidden";
      setIsTabHidden(hidden);

      const now = Date.now();
      switches.current.push(now);

      // drop old switches outside the window
      switches.current = switches.current.filter((t) => now - t <= windowMs);

      if (hidden) {
        hideStartedAt.current = now;
        focused.current = false;
      } else {
        focused.current = true;
        if (hideStartedAt.current) {
          const dur = now - hideStartedAt.current;
          setLastHiddenDurationMs(dur);

          if (dur >= longHideMs) {
            onSuspicious?.("tab_hidden_too_long", { durationMs: dur });
          }
          hideStartedAt.current = null;
        }
      }

      if (switches.current.length >= maxSwitchesPerWindow) {
        onSuspicious?.("rapid_tab_switching", {
          count: switches.current.length,
          windowMs,
        });
      }
    };

    const onBlur = () => {
      focused.current = false;
      // blur fires even if tab still visible (e.g., alt-tab). Count it too.
      const now = Date.now();
      switches.current.push(now);
      switches.current = switches.current.filter((t) => now - t <= windowMs);

      if (switches.current.length >= maxSwitchesPerWindow) {
        onSuspicious?.("rapid_window_blur", {
          count: switches.current.length,
          windowMs,
        });
      }
    };

    const onFocus = () => {
      focused.current = true;
    };

    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("blur", onBlur);
    window.addEventListener("focus", onFocus);

    return () => {
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("blur", onBlur);
      window.removeEventListener("focus", onFocus);
    };
  }, [longHideMs, maxSwitchesPerWindow, windowMs, onSuspicious]);

  return {
    isTabHidden,
    lastHiddenDurationMs,
  };
}
