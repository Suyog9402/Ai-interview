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
import { apiClient, LoginData } from "@/lib/api";
import { toastAlert } from "@/components/alert-toast";
import { useUser } from "@/lib/user-context";

interface LoginFormProps {
  onLoginSuccess: () => void;
  onSwitchToSignup: () => void;
  isLoading?: boolean;
}

export const LoginForm = ({
  onLoginSuccess,
  onSwitchToSignup,
  isLoading = false,
}: LoginFormProps) => {
  const { setUser } = useUser();
  const [email, setEmail] = useState("");
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

    if (!email.trim()) {
      setFieldError("email", "Please enter your email address");
      hasErrors = true;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setFieldError("email", "Please enter a valid email address");
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
      const loginData: LoginData = {
        email,
        password,
      };

      const response = await apiClient.login(loginData);
      apiClient.setAuthToken(response.access_token);

      // Fetch and set user data
      const userData = await apiClient.getCurrentUser();
      setUser(userData);

      toastAlert({
        title: "Success",
        description: "Logged in successfully!",
      });

      onLoginSuccess();
    } catch (error) {
      console.log("Login error:", error); // Debug log

      let errorMessage = "Failed to login";

      if (error instanceof Error) {
        // Handle specific backend error messages
        const message = error.message.toLowerCase();
        console.log("Error message:", message); // Debug log

        if (
          message.includes("incorrect email or password") ||
          message.includes("unauthorized")
        ) {
          errorMessage =
            "❌ Invalid email or password. Please check your credentials and try again.";
        } else if (message.includes("inactive user")) {
          errorMessage =
            "❌ Your account has been deactivated. Please contact support.";
        } else if (message.includes("validation error")) {
          errorMessage = "❌ Please check your input and try again.";
        } else if (message.includes("network") || message.includes("fetch")) {
          errorMessage =
            "❌ Network error. Please check your connection and try again.";
        } else if (message.includes("401")) {
          errorMessage =
            "❌ Invalid email or password. Please check your credentials and try again.";
        } else {
          errorMessage = `❌ ${error.message}`;
        }
      }

      console.log("Final error message:", errorMessage); // Debug log

      // Set API error for fallback display
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
          <CardTitle className="text-2xl text-center">Welcome back</CardTitle>
          <CardDescription className="text-center">
            Enter your credentials to access your interview assistant
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
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
          </form>
          <div className="mt-4 text-center text-sm">
            <span className="text-muted-foreground">
              Don't have an account?{" "}
            </span>
            <button
              type="button"
              onClick={onSwitchToSignup}
              className="text-primary hover:underline"
              disabled={isLoading || isSubmitting}
            >
              Sign up
            </button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
