"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Room, RoomEvent } from "livekit-client";
import { motion } from "motion/react";
import {
  RoomAudioRenderer,
  RoomContext,
  StartAudio,
} from "@livekit/components-react";
import { toastAlert } from "./alert-toast";
import { SessionView } from "./session-view";
import { Toaster } from "./ui/sonner";
import { Welcome } from "./welcome";
import useConnectionDetails from "@/hooks/useConnectionDetails";
import type { AppConfig } from "@/lib/types";

const MotionWelcome = motion.create(Welcome);
const MotionSessionView = motion.create(SessionView);

function FullPageSpinner({ message = "Preparing your results..." }: { message?: string }) {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4" />
      <p className="text-muted-foreground text-sm">{message}</p>
    </div>
  );
}

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  const room = useMemo(() => new Room(), []);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [isProcessingAfterEndCall, setIsProcessingAfterEndCall] = useState(false);
  const processingAfterEndCallRef = useRef(false);
  const { connectionDetails, refreshConnectionDetails } =
    useConnectionDetails();

  const onEndCallStarted = () => {
    processingAfterEndCallRef.current = true;
    setIsProcessingAfterEndCall(true);
  };

  useEffect(() => {
    const onDisconnected = () => {
      if (processingAfterEndCallRef.current) return;
      setSessionStarted(false);
      refreshConnectionDetails();
    };
    const onMediaDevicesError = (error: Error) => {
      toastAlert({
        title: "Encountered an error with your media devices",
        description: `${error.name}: ${error.message}`,
      });
    };
    room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);
    room.on(RoomEvent.Disconnected, onDisconnected);
    return () => {
      room.off(RoomEvent.Disconnected, onDisconnected);
      room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
    };
  }, [room, refreshConnectionDetails]);

  useEffect(() => {
    let aborted = false;
    if (sessionStarted && room.state === "disconnected" && connectionDetails) {
      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: appConfig.isPreConnectBufferEnabled,
        }),
        room.localParticipant.setCameraEnabled(true),
        room.connect(
          connectionDetails.serverUrl,
          connectionDetails.participantToken,
        ),
      ]).catch((error) => {
        if (aborted) {
          return;
        }
        toastAlert({
          title: "There was an error connecting to the agent",
          description: `${error.name}: ${error.message}`,
        });
      });
    }
    return () => {
      aborted = true;
      room.disconnect();
    };
  }, [
    room,
    sessionStarted,
    connectionDetails,
    appConfig.isPreConnectBufferEnabled,
  ]);

  const { startButtonText } = appConfig;

  if (sessionStarted && isProcessingAfterEndCall) {
    return (
      <>
        <FullPageSpinner />
        <Toaster />
      </>
    );
  }

  return (
    <>
      {!sessionStarted && (
        <MotionWelcome
          key="welcome"
          startButtonText={startButtonText}
          onStartCall={() => setSessionStarted(true)}
          disabled={sessionStarted}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5, ease: "linear" }}
        />
      )}

      {sessionStarted && (
        <RoomContext.Provider value={room}>
          <RoomAudioRenderer />
          <StartAudio label="Start Audio" />
          <MotionSessionView
            key="session-view"
            appConfig={appConfig}
            disabled={!sessionStarted}
            sessionStarted={sessionStarted}
            onEndCallStarted={onEndCallStarted}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: "linear" }}
          />
        </RoomContext.Provider>
      )}

      <Toaster />
    </>
  );
}
