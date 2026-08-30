"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Upload, FileText } from "lucide-react";
import { apiClient } from "@/lib/api";
import { toast } from "sonner";

export default function CreateJDPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    content: "",
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [inputMethod, setInputMethod] = useState<"textarea" | "file">("textarea");

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.txt')) {
        toast.error("Only .txt files are allowed");
        return;
      }
      setSelectedFile(file);
      // Preview file content
      try {
        const text = await file.text();
        setFormData(prev => ({ ...prev, content: text }));
      } catch (error) {
        toast.error("Failed to read file. Please ensure it's a valid text file.");
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      toast.error("Title is required");
      return;
    }

    if (inputMethod === "file" && !selectedFile) {
      toast.error("Please select a file");
      return;
    }

    if (inputMethod === "textarea" && !formData.content.trim()) {
      toast.error("JD content is required");
      return;
    }

    try {
      setIsSubmitting(true);

      if (inputMethod === "file" && selectedFile) {
        await apiClient.uploadJDFile(
          selectedFile,
          formData.title,
          formData.description || undefined
        );
      } else {
        await apiClient.createJD({
          title: formData.title,
          description: formData.description || undefined,
          content: formData.content,
        });
      }

      toast.success("Job Description created successfully");
      router.push("/admin/jobs");
    } catch (error: any) {
      toast.error(error.message || "Failed to create JD");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Button
        variant="ghost"
        onClick={() => router.back()}
        className="mb-4"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back
      </Button>

      <div>
        <h1 className="text-4xl font-bold tracking-tight">Create Job Description</h1>
        <p className="text-muted-foreground mt-2">
          Add a new job description to the system
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) =>
                  setFormData(prev => ({ ...prev, title: e.target.value }))
                }
                placeholder="e.g., Senior Frontend Developer"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData(prev => ({ ...prev, description: e.target.value }))
                }
                placeholder="Brief description of the role"
              />
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>JD Content</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={inputMethod} onValueChange={(v) => setInputMethod(v as any)}>
              <TabsList>
                <TabsTrigger value="textarea">
                  <FileText className="h-4 w-4 mr-2" />
                  Text Input
                </TabsTrigger>
                <TabsTrigger value="file">
                  <Upload className="h-4 w-4 mr-2" />
                  File Upload
                </TabsTrigger>
              </TabsList>

              <TabsContent value="textarea" className="mt-4">
                <Label htmlFor="content">Content *</Label>
                <textarea
                  id="content"
                  value={formData.content}
                  onChange={(e) =>
                    setFormData(prev => ({ ...prev, content: e.target.value }))
                  }
                  className="w-full min-h-[400px] p-3 border rounded-md font-mono text-sm mt-2"
                  placeholder="Paste or type the job description content here..."
                  required={inputMethod === "textarea"}
                />
              </TabsContent>

              <TabsContent value="file" className="mt-4">
                <Label htmlFor="file">Upload .txt file *</Label>
                <div className="mt-2 border-2 border-dashed rounded-lg p-6 text-center">
                  <input
                    type="file"
                    id="file"
                    accept=".txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <label htmlFor="file" className="cursor-pointer">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      {selectedFile ? selectedFile.name : "Click to upload or drag and drop"}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      .txt files only
                    </p>
                  </label>
                </div>
                {formData.content && (
                  <div className="mt-4">
                    <Label>Preview</Label>
                    <div className="mt-2 p-3 border rounded-md max-h-[300px] overflow-auto bg-muted/50">
                      <pre className="text-sm whitespace-pre-wrap">{formData.content}</pre>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4 mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Create JD"}
          </Button>
        </div>
      </form>
    </div>
  );
}

