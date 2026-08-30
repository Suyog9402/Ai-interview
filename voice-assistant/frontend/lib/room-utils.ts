import { Room } from "livekit-client";
import { connectionManager } from "./connection-manager";

/**
 * Safely disconnect a LiveKit room with proper state checking and error handling
 */
export async function safeDisconnect(
  room: Room,
  context: string = "unknown",
): Promise<void> {
  if (!room) {
    console.warn(`Room is null in ${context}`);
    return;
  }

  // Check if room is in a state where disconnect operations are safe
  if (!canDisconnect(room)) {
    console.log(
      `Room not in disconnectable state (${room.state}) in ${context}, skipping disconnect`,
    );
    return;
  }

  await connectionManager.safeDisconnect(room, context);
}

/**
 * Check if a room is in a state where disconnect operations are safe
 */
export function canDisconnect(room: Room): boolean {
  return room && (room.state === "connected" || room.state === "connecting");
}

/**
 * Safely connect to a LiveKit room with proper error handling
 */
export async function safeConnect(
  room: Room,
  serverUrl: string,
  token: string,
  context: string = "unknown",
): Promise<void> {
  if (!room) {
    throw new Error(`Room is null in ${context}`);
  }

  if (room.state !== "disconnected") {
    console.log(
      `Room already connected or connecting in ${context}, current state: ${room.state}`,
    );
    return;
  }

  try {
    await room.connect(serverUrl, token);
    console.log(`Successfully connected room in ${context}`);
  } catch (error) {
    console.error(`Error connecting room in ${context}:`, error);
    throw error;
  }
}
