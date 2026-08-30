"use client";

import { ReactNode } from "react";
import { UserProvider } from "@/lib/user-context";

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return <UserProvider>{children}</UserProvider>;
}
