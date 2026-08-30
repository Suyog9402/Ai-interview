import { Room } from "livekit-client";

class ConnectionManager {
  private static instance: ConnectionManager;
  private activeConnections: Map<string, Room> = new Map();
  private disconnectingRooms: Set<string> = new Set();

  private constructor() {}

  static getInstance(): ConnectionManager {
    if (!ConnectionManager.instance) {
      ConnectionManager.instance = new ConnectionManager();
    }
    return ConnectionManager.instance;
  }

  registerRoom(roomId: string, room: Room): void {
    this.activeConnections.set(roomId, room);
    console.log(`Room ${roomId} registered with connection manager`);
  }

  unregisterRoom(roomId: string): void {
    this.activeConnections.delete(roomId);
    this.disconnectingRooms.delete(roomId);
    console.log(`Room ${roomId} unregistered from connection manager`);
  }

  isDisconnecting(roomId: string): boolean {
    return this.disconnectingRooms.has(roomId);
  }

  async safeDisconnect(room: Room, context: string = "unknown"): Promise<void> {
    const roomId = this.getRoomId(room);

    if (!roomId) {
      console.warn(`Cannot identify room in ${context}`);
      return;
    }

    // Check if already disconnecting
    if (this.isDisconnecting(roomId)) {
      console.log(
        `Room ${roomId} already disconnecting in ${context}, skipping`,
      );
      return;
    }

    // Check if room is in a valid state for disconnect
    if (room.state !== "connected" && room.state !== "connecting") {
      console.log(
        `Room ${roomId} not in connected state (${room.state}) in ${context}, skipping disconnect`,
      );
      this.unregisterRoom(roomId); // Clean up registration even if not connected
      return;
    }

    // Mark as disconnecting
    this.disconnectingRooms.add(roomId);

    try {
      console.log(`Disconnecting room ${roomId} in ${context}`);

      // Add a small delay to ensure any pending operations complete
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Check state again before attempting disconnect
      if (room.state === "connected" || room.state === "connecting") {
        await room.disconnect();
        console.log(`Successfully disconnected room ${roomId} in ${context}`);
      } else {
        console.log(
          `Room ${roomId} state changed to ${room.state} before disconnect in ${context}`,
        );
      }
    } catch (error) {
      console.warn(`Error disconnecting room ${roomId} in ${context}:`, error);
      // Don't re-throw the error as it might be expected in some cases
    } finally {
      // Clean up
      this.disconnectingRooms.delete(roomId);
      this.unregisterRoom(roomId);
    }
  }

  private getRoomId(room: Room): string | null {
    // Try to get room name or create a unique identifier
    if (room.name) {
      return room.name;
    }

    // Fallback to using room instance as key
    for (const [roomId, registeredRoom] of this.activeConnections.entries()) {
      if (registeredRoom === room) {
        return roomId;
      }
    }

    return null;
  }

  getActiveConnectionsCount(): number {
    return this.activeConnections.size;
  }

  getDisconnectingCount(): number {
    return this.disconnectingRooms.size;
  }

  // Force cleanup for all rooms (useful for app shutdown)
  async cleanupAll(): Promise<void> {
    console.log(
      `Cleaning up ${this.activeConnections.size} active connections`,
    );

    const disconnectPromises = Array.from(this.activeConnections.values()).map(
      (room) => this.safeDisconnect(room, "cleanup-all"),
    );

    await Promise.allSettled(disconnectPromises);
    this.activeConnections.clear();
    this.disconnectingRooms.clear();
  }
}

export const connectionManager = ConnectionManager.getInstance();
