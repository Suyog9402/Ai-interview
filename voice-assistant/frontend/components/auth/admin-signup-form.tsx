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

interface AdminSignupFormProps {
  onSignupSuccess: () => void;
  isLoading?: boolean;
}

export const AdminSignupForm = ({
  onSignupSuccess,
  isLoading = false,
}: AdminSignupFormProps) => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
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

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearErrors();

    // Client-side validation
    let hasErrors = false;

    if (!username.trim()) {
      setFieldError("username", "Please enter a username");
      hasErrors = true;
    } else if (username.trim().length < 3) {
      setFieldError("username", "Username must be at least 3 characters");
      hasErrors = true;
    }

    if (!email.trim()) {
      setFieldError("email", "Please enter your email");
      hasErrors = true;
    } else if (!validateEmail(email)) {
      setFieldError("email", "Please enter a valid email address");
      hasErrors = true;
    }

    if (!password.trim()) {
      setFieldError("password", "Please enter a password");
      hasErrors = true;
    } else if (password.length < 8) {
      setFieldError("password", "Password must be at least 8 characters");
      hasErrors = true;
    }

    if (!confirmPassword.trim()) {
      setFieldError("confirmPassword", "Please confirm your password");
      hasErrors = true;
    } else if (password !== confirmPassword) {
      setFieldError("confirmPassword", "Passwords do not match");
      hasErrors = true;
    }

    if (hasErrors) {
      return;
    }

    setIsSubmitting(true);

    try {
      await apiClient.adminSignup(username, email, password);

      toastAlert({
        title: "Success",
        description: "Admin account created successfully!",
      });

      onSignupSuccess();
    } catch (error) {
      console.log("Admin signup error:", error);

      let errorMessage = "Failed to create admin account";

      if (error instanceof Error) {
        const message = error.message.toLowerCase();

        if (
          message.includes("username or email already exists") ||
          message.includes("already exists")
        ) {
          errorMessage =
            "❌ Username or email already exists. Please use different credentials.";
        } else if (
          message.includes("admin signup is only allowed when no admins exist")
        ) {
          errorMessage =
            "❌ Admin signup is only available for the first admin. Please contact an existing admin to create your account.";
        } else if (message.includes("network") || message.includes("fetch")) {
          errorMessage =
            "❌ Network error. Please check your connection and try again.";
        } else {
          errorMessage = `❌ ${error.message}`;
        }
      }

      setApiError(errorMessage);

      toastAlert({
        title: "Signup Failed",
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
          <CardTitle className="text-2xl text-center">Admin Signup</CardTitle>
          <CardDescription className="text-center">
            Create a new admin account to access the dashboard
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
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading || isSubmitting}
                className={errors.email ? "border-red-500" : ""}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password (min. 8 characters)"
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
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={isLoading || isSubmitting}
                className={errors.confirmPassword ? "border-red-500" : ""}
              />
              {errors.confirmPassword && (
                <p className="text-sm text-red-500">{errors.confirmPassword}</p>
              )}
            </div>
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || isSubmitting}
            >
              {isSubmitting ? "Creating account..." : "Create Admin Account"}
            </Button>

            {/* Fallback API Error Display */}
            {apiError && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{apiError}</p>
              </div>
            )}

            <div className="text-center text-sm text-muted-foreground mt-4">
              Already have an admin account?{" "}
              <Link
                href="/admin/login"
                className="text-primary hover:underline font-medium"
              >
                Sign in
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
};

