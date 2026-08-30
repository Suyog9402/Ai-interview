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
import { apiClient, SignupData } from "@/lib/api";
import { toastAlert } from "@/components/alert-toast";

interface SignupFormProps {
  onSignupSuccess: () => void;
  onSwitchToLogin: () => void;
  isLoading?: boolean;
}

export const SignupForm = ({
  onSignupSuccess,
  onSwitchToLogin,
  isLoading = false,
}: SignupFormProps) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [username, setUsername] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const clearErrors = () => {
    setErrors({});
  };

  const setFieldError = (field: string, message: string) => {
    setErrors((prev) => ({ ...prev, [field]: message }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearErrors();

    // Client-side validation
    let hasErrors = false;

    if (!name.trim()) {
      setFieldError("name", "Please enter your full name");
      hasErrors = true;
    }

    if (!username.trim()) {
      setFieldError("username", "Please enter a username");
      hasErrors = true;
    } else if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
      setFieldError(
        "username",
        "Username must be 3-20 characters and contain only letters, numbers, and underscores",
      );
      hasErrors = true;
    }

    if (!email.trim()) {
      setFieldError("email", "Please enter your email address");
      hasErrors = true;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setFieldError("email", "Please enter a valid email address");
      hasErrors = true;
    }

    if (password.length < 8) {
      setFieldError("password", "Password must be at least 8 characters long");
      hasErrors = true;
    }

    if (password !== confirmPassword) {
      setFieldError("confirmPassword", "Passwords do not match");
      hasErrors = true;
    }

    if (hasErrors) {
      return;
    }

    setIsSubmitting(true);
    try {
      const signupData: SignupData = {
        email,
        username,
        password,
        full_name: name,
      };

      await apiClient.signup(signupData);
      toastAlert({
        title: "Success",
        description: "Account created successfully! Please sign in.",
      });
      onSignupSuccess();
    } catch (error) {
      console.log("Signup error:", error); // Debug log

      let errorMessage = "Failed to create account";

      if (error instanceof Error) {
        // Handle specific backend error messages
        const message = error.message.toLowerCase();
        console.log("Error message:", message); // Debug log

        if (message.includes("email already registered")) {
          errorMessage =
            "❌ This email is already registered. Please use a different email or try logging in.";
        } else if (message.includes("username already taken")) {
          errorMessage =
            "❌ This username is already taken. Please choose a different username.";
        } else if (message.includes("password must be at least 8 characters")) {
          errorMessage = "❌ Password must be at least 8 characters long.";
        } else if (message.includes("username must be 3-20 characters")) {
          errorMessage =
            "❌ Username must be 3-20 characters and contain only letters, numbers, and underscores.";
        } else if (message.includes("validation error")) {
          errorMessage = "❌ Please check your input and try again.";
        } else if (message.includes("400")) {
          errorMessage = "❌ Please check your input and try again.";
        } else {
          errorMessage = `❌ ${error.message}`;
        }
      }

      console.log("Final error message:", errorMessage); // Debug log

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
          <CardTitle className="text-2xl text-center">Create account</CardTitle>
          <CardDescription className="text-center">
            Sign up to start your AI-powered interview journey
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Enter your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={isLoading || isSubmitting}
                className={errors.name ? "border-red-500" : ""}
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name}</p>
              )}
            </div>
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
                placeholder="Create a password (min 8 characters)"
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
              {isSubmitting ? "Creating account..." : "Create account"}
            </Button>
          </form>
          <div className="mt-4 text-center text-sm">
            <span className="text-muted-foreground">
              Already have an account?{" "}
            </span>
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="text-primary hover:underline"
              disabled={isLoading || isSubmitting}
            >
              Sign in
            </button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
