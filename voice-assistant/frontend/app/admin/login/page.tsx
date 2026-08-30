"use client";
import { useRouter } from "next/navigation";
import { AdminLoginForm } from "@/components/auth/admin-login-form";
import { Toaster } from "@/components/ui/sonner";

export default function AdminLoginPage() {
  const router = useRouter();

  const handleLoginSuccess = () => {
    // After successful login, redirect to admin dashboard
    router.push("/admin/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <AdminLoginForm
        onLoginSuccess={handleLoginSuccess}
        isLoading={false}
      />
      <Toaster />
    </div>
  );
}

