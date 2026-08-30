import { useMemo } from "react";
import {
  type ReceivedChatMessage,
  type TextStreamData,
  useChat,
  useRoomContext,
  useTranscriptions,
} from "@livekit/components-react";

export default function useChatAndTranscription() {
  const transcriptions: TextStreamData[] = useTranscriptions();
  const chat = useChat();
  const room = useRoomContext();

  const mergedTranscriptions = useMemo(() => {
    const localParticipant = room?.localParticipant;
    const localIdentity = localParticipant?.identity;
    
    const merged: Array<ReceivedChatMessage> = [
      ...transcriptions.map((transcription) => {
        // Determine if this transcription is from the local user
        const isLocal = transcription.participant?.identity === localIdentity;
        
        return {
          id: transcription.streamInfo.id,
          timestamp: transcription.streamInfo.timestamp,
          message: transcription.text,
          from: {
            isLocal: isLocal,
            identity: transcription.participant?.identity,
            name: transcription.participant?.name,
          },
        };
      }),
      ...chat.chatMessages,
    ];
    return merged.sort((a, b) => a.timestamp - b.timestamp);
  }, [transcriptions, chat.chatMessages, room]);

  return { messages: mergedTranscriptions, send: chat.send };
}
