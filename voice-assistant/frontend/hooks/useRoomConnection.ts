import { useEffect, useRef, useState } from "react";
import { Room, RoomEvent } from "livekit-client";
import { safeDisconnect, safeConnect } from "@/lib/room-utils";

interface UseRoomConnectionOptions {
  serverUrl?: string;
  token?: string;
  autoConnect?: boolean;
  context?: string;
}

export function useRoomConnection(options: UseRoomConnectionOptions = {}) {
  const {
    serverUrl,
    token,
    autoConnect = false,
    context = "unknown",
  } = options;
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const roomRef = useRef<Room | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Create room instance
  useEffect(() => {
    if (!roomRef.current) {
      roomRef.current = new Room();
    }

    const room = roomRef.current;

    // Set up event listeners
    const handleConnected = () => {
      setIsConnected(true);
      setIsConnecting(false);
      setError(null);
      console.log(`Room connected in ${context}`);
    };

    const handleDisconnected = () => {
      setIsConnected(false);
      setIsConnecting(false);
      console.log(`Room disconnected in ${context}`);
    };

    const handleConnecting = () => {
      setIsConnecting(true);
      setError(null);
      console.log(`Room connecting in ${context}`);
    };

    const handleConnectionFailed = (error: Error) => {
      setIsConnecting(false);
      setIsConnected(false);
      setError(error.message);
      console.error(`Room connection failed in ${context}:`, error);
    };

    room.on(RoomEvent.Connected, handleConnected);
    room.on(RoomEvent.Disconnected, handleDisconnected);
    // Note: LiveKit doesn't have explicit Connecting/ConnectionFailed events
    // We'll handle these states through the connection process

    // Cleanup function
    return () => {
      room.off(RoomEvent.Connected, handleConnected);
      room.off(RoomEvent.Disconnected, handleDisconnected);
    };
  }, [context]);

  // Auto-connect effect
  useEffect(() => {
    if (autoConnect && serverUrl && token && roomRef.current) {
      connect(serverUrl, token);
    }
  }, [autoConnect, serverUrl, token]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (roomRef.current) {
        safeDisconnect(roomRef.current, `${context}-cleanup`);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [context]);

  const connect = async (url: string, accessToken: string) => {
    if (!roomRef.current) {
      throw new Error("Room not initialized");
    }

    // Abort any existing connection attempt
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      setIsConnecting(true);
      setError(null);

      await safeConnect(roomRef.current, url, accessToken, context);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        console.log(`Connection aborted in ${context}`);
        return;
      }

      setError(err instanceof Error ? err.message : "Connection failed");
      setIsConnecting(false);
      throw err;
    }
  };

  const disconnect = () => {
    if (roomRef.current) {
      safeDisconnect(roomRef.current, context);
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  return {
    room: roomRef.current,
    isConnecting,
    isConnected,
    error,
    connect,
    disconnect,
  };
}
