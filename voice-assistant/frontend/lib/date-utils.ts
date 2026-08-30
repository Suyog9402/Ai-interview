// lib/date-utils.ts
// Date utility functions (fallback if date-fns is not available)

export function formatDistanceToNow(date: Date, options?: { addSuffix?: boolean }): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  let result = "";
  if (diffDays > 0) {
    result = `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
  } else if (diffHours > 0) {
    result = `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  } else if (diffMins > 0) {
    result = `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;
  } else {
    result = "just now";
  }

  if (options?.addSuffix === false) {
    return result.replace(" ago", "");
  }

  return result;
}

