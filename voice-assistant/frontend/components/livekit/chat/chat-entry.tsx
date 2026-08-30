import * as React from "react";
import type {
  MessageFormatter,
  ReceivedChatMessage,
} from "@livekit/components-react";
import { cn } from "@/lib/utils";
import { useChatMessage } from "./hooks/utils";

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The chat massage object to display. */
  entry: ReceivedChatMessage;
  /** Hide sender name. Useful when displaying multiple consecutive chat messages from the same person. */
  hideName?: boolean;
  /** Hide message timestamp. */
  hideTimestamp?: boolean;
  /** An optional formatter for the message body. */
  messageFormatter?: MessageFormatter;
}

export const ChatEntry = ({
  entry,
  messageFormatter,
  hideName,
  hideTimestamp,
  className,
  ...props
}: ChatEntryProps) => {
  const { message, hasBeenEdited, time, locale, name } = useChatMessage(
    entry,
    messageFormatter,
  );

  const isUser = entry.from?.isLocal ?? false;
  const messageOrigin = isUser ? "remote" : "local";

  return (
    <li
      data-lk-message-origin={messageOrigin}
      title={time.toLocaleTimeString(locale, { timeStyle: "full" })}
      className={cn("group flex flex-col gap-2 mb-6 w-full", className)}
      {...props}
    >
      {(!hideTimestamp || !hideName || hasBeenEdited) && (
        <span
          className={cn(
            "text-muted-foreground flex text-sm",
            isUser ? "justify-end" : "justify-start",
          )}
        >
          {!hideName && <strong className="font-semibold">{name}</strong>}

          {!hideTimestamp && (
            <span className="align-self-end ml-2 font-mono text-xs opacity-70">
              {hasBeenEdited && "*"}
              {time.toLocaleTimeString(locale, { timeStyle: "short" })}
            </span>
          )}
        </span>
      )}

      <div
        className={cn(
          "w-full max-w-4/5 rounded-[20px] p-3 text-base leading-relaxed shadow-sm min-h-[50px] flex items-center",
          isUser
            ? "bg-blue-100 text-blue-900 border border-blue-200 ml-auto"
            : "bg-gray-100 text-gray-900 border border-gray-200 mr-auto",
        )}
      >
        <span className="w-full">{message}</span>
      </div>
    </li>
  );
};
