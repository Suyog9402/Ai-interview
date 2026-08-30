"use client";
import { useRouter } from "next/navigation";
import { AdminSignupForm } from "@/components/auth/admin-signup-form";
import { Toaster } from "@/components/ui/sonner";

export default function AdminSignupPage() {
  const router = useRouter();

  const handleSignupSuccess = () => {
    // After successful signup, redirect to admin login
    router.push("/admin/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <AdminSignupForm
        onSignupSuccess={handleSignupSuccess}
        isLoading={false}
      />
      <Toaster />
    </div>
  );
}

