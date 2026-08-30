"use client";
import { useRouter } from "next/navigation";
import { SignupForm } from "@/components/auth/signup-form";
import { Toaster } from "@/components/ui/sonner";

export default function SignupPage() {
  const router = useRouter();

  const handleSignupSuccess = () => {
    // After successful signup, redirect to login
    router.push("/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <SignupForm
        onSignupSuccess={handleSignupSuccess}
        onSwitchToLogin={() => router.push("/login")}
        isLoading={false}
      />
      <Toaster />
    </div>
  );
}
