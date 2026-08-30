"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiClient } from "@/lib/api";
import { toastAlert } from "@/components/alert-toast";
import Link from "next/link";

interface AdminLoginFormProps {
  onLoginSuccess: () => void;
  isLoading?: boolean;
}

export const AdminLoginForm = ({
  onLoginSuccess,
  isLoading = false,
}: AdminLoginFormProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [apiError, setApiError] = useState<string>("");

  const clearErrors = () => {
    setErrors({});
    setApiError("");
  };

  const setFieldError = (field: string, message: string) => {
    setErrors((prev) => ({ ...prev, [field]: message }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearErrors();

    // Client-side validation
    let hasErrors = false;

    if (!username.trim()) {
      setFieldError("username", "Please enter your username");
      hasErrors = true;
    }

    if (!password.trim()) {
      setFieldError("password", "Please enter your password");
      hasErrors = true;
    }

    if (hasErrors) {
      return;
    }

    setIsSubmitting(true);

    try {
      await apiClient.adminLogin(username, password);

      toastAlert({
        title: "Success",
        description: "Admin login successful!",
      });

      onLoginSuccess();
    } catch (error) {
      console.log("Admin login error:", error);

      let errorMessage = "Failed to login";

      if (error instanceof Error) {
        const message = error.message.toLowerCase();

        if (
          message.includes("incorrect username or password") ||
          message.includes("unauthorized")
        ) {
          errorMessage =
            "❌ Invalid username or password. Please check your credentials and try again.";
        } else if (message.includes("inactive")) {
          errorMessage =
            "❌ Your admin account has been deactivated. Please contact support.";
        } else if (message.includes("network") || message.includes("fetch")) {
          errorMessage =
            "❌ Network error. Please check your connection and try again.";
        } else {
          errorMessage = `❌ ${error.message}`;
        }
      }

      setApiError(errorMessage);

      toastAlert({
        title: "Login Failed",
        description: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md"
    >
      <Card className="w-full">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center">Admin Login</CardTitle>
          <CardDescription className="text-center">
            Enter your admin credentials to access the dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={isLoading || isSubmitting}
                className={errors.username ? "border-red-500" : ""}
              />
              {errors.username && (
                <p className="text-sm text-red-500">{errors.username}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading || isSubmitting}
                className={errors.password ? "border-red-500" : ""}
              />
              {errors.password && (
                <p className="text-sm text-red-500">{errors.password}</p>
              )}
            </div>
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || isSubmitting}
            >
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>

            {/* Fallback API Error Display */}
            {apiError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{apiError}</p>
              </div>
            )}

            <div className="text-center text-sm text-muted-foreground mt-4">
              Don't have an admin account?{" "}
              <Link
                href="/admin/signup"
                className="text-primary hover:underline font-medium"
              >
                Sign up
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
};

