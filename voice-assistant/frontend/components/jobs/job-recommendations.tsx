"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Building,
  MapPin,
  CurrencyDollar,
  Star,
  CheckCircle,
  XCircle,
  Lightbulb,
  CaretDown,
  CaretUp,
  FileText,
} from "@phosphor-icons/react";

interface JobRecommendation {
  id: number;
  title: string;
  company: string;
  location: string;
  salary: string;
  match: number;
  description: string;
  fullAnalysis?: string;
  keyMatches?: string[];
  missingSkills?: string[];
  recommendations?: string;
  jdSource?: string;
}

interface JobRecommendationsProps {
  jobs: JobRecommendation[];
  onJobSelect?: (job: JobRecommendation) => void;
}

export const JobRecommendations = ({
  jobs,
  onJobSelect,
}: JobRecommendationsProps) => {
  const [expandedJob, setExpandedJob] = useState<number | null>(null);
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<number>>(new Set());

  const toggleExpanded = (jobId: number) => {
    setExpandedJob(expandedJob === jobId ? null : jobId);
  };

  const toggleDescription = (jobId: number) => {
    setExpandedDescriptions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
      } else {
        newSet.add(jobId);
      }
      return newSet;
    });
  };

  const isDescriptionExpanded = (jobId: number) => {
    return expandedDescriptions.has(jobId);
  };

  const getMatchColor = (match: number) => {
    if (match >= 80) return "bg-green-100 text-green-800 border-green-200";
    if (match >= 60) return "bg-yellow-100 text-yellow-800 border-yellow-200";
    return "bg-red-100 text-red-800 border-red-200";
  };

  const getMatchIcon = (match: number) => {
    if (match >= 80) return <CheckCircle className="h-4 w-4" />;
    if (match >= 60) return <Star className="h-4 w-4" />;
    return <XCircle className="h-4 w-4" />;
  };

  if (jobs.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-4xl mx-auto"
      >
        <Card className="w-full">
          <CardContent className="p-8 text-center">
            <div className="space-y-4">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900">
                No Job Matches Found
              </h3>
              <p className="text-gray-500">
                We couldn't find any job descriptions that match your resume
                with 65% or higher compatibility. Try uploading a different
                resume or check back later for new opportunities.
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-4xl mx-auto space-y-3 sm:space-y-6 px-2 sm:px-0"
    >
      <div className="text-center mb-3 sm:mb-6">
        <h2 className="text-lg sm:text-2xl font-bold text-gray-900 mb-1 sm:mb-2">
          AI-Powered Job Recommendations
        </h2>
        <p className="text-xs sm:text-base text-gray-600">
          Found {jobs.length} job(s) that match your resume with 65%+
          compatibility
        </p>
      </div>

      <div className="grid gap-3 sm:gap-6">
        {jobs.map((job, index) => (
          <motion.div
            key={job.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Card className="w-full hover:shadow-lg transition-shadow border border-gray-200">
              <CardHeader className="p-3 sm:p-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-start justify-between gap-2 sm:gap-4">
                  <div className="flex-1 w-full">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-1.5 sm:gap-3 mb-1.5 sm:mb-2">
                      <CardTitle className="text-base sm:text-xl break-words leading-tight">{job.title}</CardTitle>
                      <Badge
                        className={`${getMatchColor(job.match)} flex items-center gap-1 shrink-0 text-xs px-1.5 py-0.5`}
                      >
                        {getMatchIcon(job.match)}
                        <span className="text-xs">{job.match}%</span>
                      </Badge>
                    </div>

                    <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-4 text-xs sm:text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Building className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
                        <span className="break-words text-xs sm:text-sm">{job.company}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
                        <span className="text-xs sm:text-sm">{job.location}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <CurrencyDollar className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
                        <span className="text-xs sm:text-sm">{job.salary}</span>
                      </div>
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleExpanded(job.id)}
                    className="sm:ml-4 self-start sm:self-center h-8 w-8 p-0"
                  >
                    {expandedJob === job.id ? (
                      <CaretUp className="h-3 w-3 sm:h-4 sm:w-4" />
                    ) : (
                      <CaretDown className="h-3 w-3 sm:h-4 sm:w-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="space-y-2 sm:space-y-4 p-3 sm:p-6 pt-0">
                <div className="space-y-2">
                  <p className={`text-sm sm:text-base text-gray-700 ${!isDescriptionExpanded(job.id) ? 'line-clamp-2' : ''}`}>
                    {job.description}
                  </p>
                  {job.description.length > 150 && (
                    <button
                      onClick={() => toggleDescription(job.id)}
                      className="text-xs sm:text-sm text-blue-600 hover:text-blue-800 font-medium underline-offset-2 hover:underline transition-colors"
                    >
                      {isDescriptionExpanded(job.id) ? 'Read Less' : 'Read More'}
                    </button>
                  )}
                </div>

                {expandedJob === job.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-3 sm:space-y-6 pt-2 sm:pt-4 border-t"
                  >
                    {/* AI Analysis */}
                    {job.fullAnalysis && (
                      <div className="space-y-2 sm:space-y-3">
                        <h4 className="font-semibold text-sm sm:text-base text-gray-900 flex items-center gap-1.5 sm:gap-2">
                          <Lightbulb className="h-3 w-3 sm:h-4 sm:w-4" />
                          AI Analysis
                        </h4>
                        <div className="bg-blue-50 p-2 sm:p-4 rounded-lg">
                          <p className="text-xs sm:text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                            {job.fullAnalysis}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Key Matches */}
                    {job.keyMatches && job.keyMatches.length > 0 && (
                      <div className="space-y-2 sm:space-y-3">
                        <h4 className="font-semibold text-sm sm:text-base text-gray-900 flex items-center gap-1.5 sm:gap-2">
                          <CheckCircle className="h-3 w-3 sm:h-4 sm:w-4 text-green-600" />
                          Key Matches
                        </h4>
                        <div className="flex flex-wrap gap-1.5 sm:gap-2">
                          {job.keyMatches.map((skill, idx) => (
                            <Badge
                              key={idx}
                              variant="secondary"
                              className="bg-green-100 text-green-800 text-xs px-1.5 py-0.5"
                            >
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Skills */}
                    {job.missingSkills && job.missingSkills.length > 0 && (
                      <div className="space-y-2 sm:space-y-3">
                        <h4 className="font-semibold text-sm sm:text-base text-gray-900 flex items-center gap-1.5 sm:gap-2">
                          <XCircle className="h-3 w-3 sm:h-4 sm:w-4 text-red-600" />
                          Skills to Develop
                        </h4>
                        <div className="flex flex-wrap gap-1.5 sm:gap-2">
                          {job.missingSkills.map((skill, idx) => (
                            <Badge
                              key={idx}
                              variant="outline"
                              className="border-red-200 text-red-700 text-xs px-1.5 py-0.5"
                            >
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendations */}
                    {job.recommendations && (
                      <div className="space-y-2 sm:space-y-3">
                        <h4 className="font-semibold text-sm sm:text-base text-gray-900 flex items-center gap-1.5 sm:gap-2">
                          <Lightbulb className="h-3 w-3 sm:h-4 sm:w-4 text-yellow-600" />
                          Recommendations
                        </h4>
                        <div className="bg-yellow-50 p-2 sm:p-4 rounded-lg">
                          <p className="text-xs sm:text-sm text-gray-700">
                            {job.recommendations}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-2 sm:pt-4">
                      <Button
                        onClick={() => onJobSelect?.(job)}
                        className="w-full sm:flex-1 h-9 sm:h-10 text-sm"
                      >
                        Start AI Interview
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() =>
                          window.open(
                            `/api/v1/resume/jd/${job.jdSource}`,
                            "_blank",
                          )
                        }
                        className="w-full sm:w-auto h-9 sm:h-10 text-sm"
                      >
                        View Full JD
                      </Button>
                    </div>
                  </motion.div>
                )}

                {expandedJob !== job.id && (
                  <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                    <Button
                      onClick={() => onJobSelect?.(job)}
                      className="w-full sm:flex-1 h-9 sm:h-10 text-sm"
                    >
                      Start AI Interview
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => toggleExpanded(job.id)}
                      className="w-full sm:w-auto h-9 sm:h-10 text-sm"
                    >
                      View Details
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};
