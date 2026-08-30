"use client";

import { cva } from "class-variance-authority";
import { LocalAudioTrack, LocalVideoTrack } from "livekit-client";
import { useMaybeRoomContext } from "@livekit/components-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import React from "react";

type DeviceSelectProps = React.ComponentProps<typeof SelectTrigger> & {
  kind: MediaDeviceKind;
  track?: LocalAudioTrack | LocalVideoTrack | undefined;
  requestPermissions?: boolean;
  onMediaDeviceError?: (error: Error) => void;
  initialSelection?: string;
  onActiveDeviceChange?: (deviceId: string) => void;
  onDeviceListChange?: (devices: MediaDeviceInfo[]) => void;
  variant?: "default" | "small";
};

const selectVariants = cva(
  [
    "w-full rounded-full px-3 py-2 text-sm cursor-pointer",
    "disabled:not-allowed hover:bg-button-hover focus:bg-button-hover",
  ],
  {
    variants: {
      size: {
        default: "w-[180px]",
        sm: "w-auto",
      },
    },
    defaultVariants: {
      size: "default",
    },
  },
);

export function DeviceSelect({
  kind,
  track,
  requestPermissions,
  onMediaDeviceError,
  initialSelection,
  onActiveDeviceChange,
  onDeviceListChange,
  ...props
}: DeviceSelectProps) {
  // Temporarily disable the entire component to prevent infinite loops
  console.log("DeviceSelect rendered for kind:", kind);
  return null;

  /*
  const size = props.size || 'default';

  const room = useMaybeRoomContext();

  // Memoize the room to prevent infinite re-renders
  const memoizedRoom = React.useMemo(() => room, [room]);

  // Use a simpler approach to avoid the useMediaDeviceSelect hook issues
  const [devices, setDevices] = React.useState<MediaDeviceInfo[]>([]);
  const [activeDeviceId, setActiveDeviceId] = React.useState<string>('');
  const hasLoaded = React.useRef(false);
  const currentDeviceId = React.useRef<string>('');

  // Load devices on mount
  React.useEffect(() => {
    if (hasLoaded.current) return;

    const loadDevices = async () => {
      try {
        const mediaDevices = await navigator.mediaDevices.enumerateDevices();
        const filteredDevices = mediaDevices.filter(device => device.kind === kind);
        setDevices(filteredDevices);

        // Set default device if available
        if (filteredDevices.length > 0 && !activeDeviceId) {
          const defaultDevice = filteredDevices.find(device => device.deviceId === 'default') || filteredDevices[0];
          setActiveDeviceId(defaultDevice.deviceId);
          currentDeviceId.current = defaultDevice.deviceId;
        }
        hasLoaded.current = true;
      } catch (error) {
        // Call the error callback directly instead of using memoizedOnError
        if (onMediaDeviceError) {
          onMediaDeviceError(error as Error);
        }
      }
    };

    loadDevices();
  }, [kind]); // Remove memoizedOnError from dependencies

  // Simplified device change handling to prevent infinite loops
  const handleDeviceChange = React.useCallback((deviceId: string) => {
    // Temporarily disable device change to prevent infinite loops
    console.log('Device change requested:', deviceId);
    return;
    
    if (deviceId && deviceId !== currentDeviceId.current) {
      setActiveDeviceId(deviceId);
      currentDeviceId.current = deviceId;
      // Only call the callback if it's provided and the device actually changed
      if (onActiveDeviceChange && deviceId !== '') {
        // Use setTimeout to prevent immediate re-renders
        setTimeout(() => {
          onActiveDeviceChange(deviceId);
        }, 0);
      }
    }
  }, [onActiveDeviceChange]);

  // If no devices are available, don't render the select
  if (!devices || devices.length === 0) {
    return null;
  }

  return (
    <Select value={activeDeviceId || ''} onValueChange={handleDeviceChange}>
      <SelectTrigger className={cn(selectVariants({ size }), props.className)}>
        {size !== 'sm' && (
          <SelectValue className="font-mono text-sm" placeholder={`Select a ${kind}`} />
        )}
      </SelectTrigger>
      <SelectContent>
        {devices.map((device) => (
          <SelectItem key={device.deviceId} value={device.deviceId} className="font-mono text-xs">
            {device.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
  */
}
