"use client";
import { useRouter } from "next/navigation";
import { LoginForm } from "@/components/auth/login-form";
import { Toaster } from "@/components/ui/sonner";

export default function LoginPage() {
  const router = useRouter();

  const handleLoginSuccess = () => {
    // After successful login, redirect to resume upload
    router.push("/resume");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <LoginForm
        onLoginSuccess={handleLoginSuccess}
        onSwitchToSignup={() => router.push("/signup")}
        isLoading={false}
      />
      <Toaster />
    </div>
  );
}
