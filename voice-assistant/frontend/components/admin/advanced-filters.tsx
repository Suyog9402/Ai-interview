"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DateRangePicker } from "@/components/ui/date-range-picker";
import { RangeSlider } from "@/components/ui/range-slider";
import {
  Filter,
  X,
  Save,
  Trash2,
  Sparkles,
  TrendingUp,
  Award,
  Users,
  Calendar,
} from "lucide-react";

export interface FilterState {
  // Search
  searchQuery: string;

  // Status filters
  isActive: boolean | null;
  isVerified: boolean | null;

  // Date ranges
  registrationDateRange: { start: string; end: string };
  lastInterviewDateRange: { start: string; end: string };

  // Score ranges
  averageScoreRange: [number, number];
  bestScoreRange: [number, number];
  latestScoreRange: [number, number];
  improvementRange: [number, number];

  // Interview count
  interviewCountRange: [number, number];

  // Smart filters
  smartFilters: string[];

  // Combination logic
  combinationLogic: "AND" | "OR";
}

interface AdvancedFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onReset: () => void;
  savedPresets?: Array<{ name: string; filters: FilterState }>;
  onSavePreset?: (name: string, filters: FilterState) => void;
  onLoadPreset?: (filters: FilterState) => void;
  onDeletePreset?: (name: string) => void;
}

const SMART_FILTERS = [
  {
    id: "close_to_hire",
    label: "Close to Hire Threshold",
    description: "Scores between 65-75%",
    icon: Award,
  },
  {
    id: "high_skill_low_comm",
    label: "High Skill, Low Communication",
    description: "Strong technical, weak communication",
    icon: Users,
  },
  {
    id: "strong_improvement",
    label: "Strong Improvement Trajectory",
    description: "Significant score improvement",
    icon: TrendingUp,
  },
  {
    id: "consistent_performers",
    label: "Consistent Performers",
    description: "Low score variance, reliable",
    icon: Sparkles,
  },
];

export function AdvancedFilters({
  filters,
  onFiltersChange,
  onReset,
  savedPresets = [],
  onSavePreset,
  onLoadPreset,
  onDeletePreset,
}: AdvancedFiltersProps) {
  const [presetName, setPresetName] = React.useState("");
  const [showSaveDialog, setShowSaveDialog] = React.useState(false);

  const updateFilter = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const toggleSmartFilter = (filterId: string) => {
    const current = filters.smartFilters;
    const updated = current.includes(filterId)
      ? current.filter((id) => id !== filterId)
      : [...current, filterId];
    updateFilter("smartFilters", updated);
  };

  const hasActiveFilters = () => {
    return (
      filters.searchQuery ||
      filters.isActive !== null ||
      filters.isVerified !== null ||
      filters.registrationDateRange.start ||
      filters.registrationDateRange.end ||
      filters.lastInterviewDateRange.start ||
      filters.lastInterviewDateRange.end ||
      filters.averageScoreRange[0] !== 0 ||
      filters.averageScoreRange[1] !== 100 ||
      filters.bestScoreRange[0] !== 0 ||
      filters.bestScoreRange[1] !== 100 ||
      filters.latestScoreRange[0] !== 0 ||
      filters.latestScoreRange[1] !== 100 ||
      filters.improvementRange[0] !== -100 ||
      filters.improvementRange[1] !== 100 ||
      filters.interviewCountRange[0] !== 0 ||
      filters.interviewCountRange[1] !== 1000 ||
      filters.smartFilters.length > 0
    );
  };

  const handleSavePreset = () => {
    if (presetName.trim() && onSavePreset) {
      onSavePreset(presetName.trim(), filters);
      setPresetName("");
      setShowSaveDialog(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Advanced Filters
          </CardTitle>
          <div className="flex items-center gap-2">
            {hasActiveFilters() && (
              <Button variant="ghost" size="sm" onClick={onReset}>
                <X className="h-4 w-4 mr-2" />
                Clear All
              </Button>
            )}
            {onSavePreset && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSaveDialog(true)}
                disabled={!hasActiveFilters()}
              >
                <Save className="h-4 w-4 mr-2" />
                Save Preset
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Saved Presets */}
        {savedPresets.length > 0 && (
          <div>
            <label className="text-sm font-medium mb-2 block">
              Saved Presets
            </label>
            <div className="flex flex-wrap gap-2">
              {savedPresets.map((preset) => (
                <Badge
                  key={preset.name}
                  variant="secondary"
                  className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                  onClick={() => onLoadPreset?.(preset.filters)}
                >
                  {preset.name}
                  {onDeletePreset && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeletePreset(preset.name);
                      }}
                      className="ml-2 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Save Preset Dialog */}
        {showSaveDialog && (
          <div className="p-4 border rounded-lg bg-muted">
            <Input
              placeholder="Preset name..."
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSavePreset();
                if (e.key === "Escape") setShowSaveDialog(false);
              }}
              className="mb-2"
              autoFocus
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={handleSavePreset}>
                Save
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setShowSaveDialog(false);
                  setPresetName("");
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Search */}
        <div>
          <label className="text-sm font-medium mb-2 block">Search</label>
          <Input
            placeholder="Search by email, username, or name..."
            value={filters.searchQuery}
            onChange={(e) => updateFilter("searchQuery", e.target.value)}
          />
        </div>

        {/* Status Filters */}
        <div>
          <label className="text-sm font-medium mb-2 block">Status</label>
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={filters.isActive === null ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilter("isActive", null)}
            >
              All Status
            </Button>
            <Button
              variant={filters.isActive === true ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilter("isActive", true)}
            >
              Active
            </Button>
            <Button
              variant={filters.isActive === false ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilter("isActive", false)}
            >
              Inactive
            </Button>
            <Button
              variant={filters.isVerified === true ? "default" : "outline"}
              size="sm"
              onClick={() =>
                updateFilter("isVerified", filters.isVerified === true ? null : true)
              }
            >
              Verified
            </Button>
          </div>
        </div>

        {/* Date Ranges */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <DateRangePicker
            label="Registration Date"
            startDate={filters.registrationDateRange.start}
            endDate={filters.registrationDateRange.end}
            onStartDateChange={(date) =>
              updateFilter("registrationDateRange", {
                ...filters.registrationDateRange,
                start: date,
              })
            }
            onEndDateChange={(date) =>
              updateFilter("registrationDateRange", {
                ...filters.registrationDateRange,
                end: date,
              })
            }
          />
          <DateRangePicker
            label="Last Interview Date"
            startDate={filters.lastInterviewDateRange.start}
            endDate={filters.lastInterviewDateRange.end}
            onStartDateChange={(date) =>
              updateFilter("lastInterviewDateRange", {
                ...filters.lastInterviewDateRange,
                start: date,
              })
            }
            onEndDateChange={(date) =>
              updateFilter("lastInterviewDateRange", {
                ...filters.lastInterviewDateRange,
                end: date,
              })
            }
          />
        </div>

        {/* Score Ranges */}
        <div className="space-y-4">
          <label className="text-sm font-medium block">Score Ranges</label>
          <RangeSlider
            label="Average Score"
            min={0}
            max={100}
            value={filters.averageScoreRange}
            onChange={(value) => updateFilter("averageScoreRange", value)}
            formatValue={(v) => `${v}%`}
          />
          <RangeSlider
            label="Best Score"
            min={0}
            max={100}
            value={filters.bestScoreRange}
            onChange={(value) => updateFilter("bestScoreRange", value)}
            formatValue={(v) => `${v}%`}
          />
          <RangeSlider
            label="Latest Score"
            min={0}
            max={100}
            value={filters.latestScoreRange}
            onChange={(value) => updateFilter("latestScoreRange", value)}
            formatValue={(v) => `${v}%`}
          />
          <RangeSlider
            label="Improvement"
            min={-100}
            max={100}
            value={filters.improvementRange}
            onChange={(value) => updateFilter("improvementRange", value)}
            formatValue={(v) => `${v > 0 ? "+" : ""}${v}%`}
          />
        </div>

        {/* Interview Count Range */}
        <RangeSlider
          label="Interview Count"
          min={0}
          max={100}
          value={filters.interviewCountRange}
          onChange={(value) => updateFilter("interviewCountRange", value)}
          formatValue={(v) => `${v} interviews`}
        />

        {/* Smart Filters */}
        <div>
          <label className="text-sm font-medium mb-2 block flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Smart Filters
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {SMART_FILTERS.map((filter) => {
              const Icon = filter.icon;
              const isActive = filters.smartFilters.includes(filter.id);
              return (
                <button
                  key={filter.id}
                  onClick={() => toggleSmartFilter(filter.id)}
                  className={`
                    p-3 border rounded-lg text-left transition-colors
                    ${
                      isActive
                        ? "border-primary bg-primary/10"
                        : "border-border hover:bg-muted"
                    }
                  `}
                >
                  <div className="flex items-start gap-2">
                    <Icon className="h-4 w-4 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-sm">{filter.label}</div>
                      <div className="text-xs text-muted-foreground">
                        {filter.description}
                      </div>
                    </div>
                    {isActive && (
                      <Badge variant="default" className="text-xs">
                        Active
                      </Badge>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Combination Logic */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            Filter Combination Logic
          </label>
          <div className="flex gap-2">
            <Button
              variant={filters.combinationLogic === "AND" ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilter("combinationLogic", "AND")}
            >
              AND (All filters must match)
            </Button>
            <Button
              variant={filters.combinationLogic === "OR" ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilter("combinationLogic", "OR")}
            >
              OR (Any filter can match)
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {filters.combinationLogic === "AND"
              ? "Users must match ALL selected filters"
              : "Users matching ANY selected filter will be shown"}
          </p>
        </div>

        {/* Active Filters Summary */}
        {hasActiveFilters() && (
          <div className="pt-4 border-t">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-medium">Active Filters:</span>
              <Badge variant="secondary">
                {[
                  filters.searchQuery && "Search",
                  filters.isActive !== null && "Status",
                  filters.isVerified !== null && "Verified",
                  (filters.registrationDateRange.start ||
                    filters.registrationDateRange.end) &&
                    "Registration Date",
                  (filters.lastInterviewDateRange.start ||
                    filters.lastInterviewDateRange.end) &&
                    "Last Interview",
                  (filters.averageScoreRange[0] !== 0 ||
                    filters.averageScoreRange[1] !== 100) &&
                    "Avg Score",
                  (filters.bestScoreRange[0] !== 0 ||
                    filters.bestScoreRange[1] !== 100) &&
                    "Best Score",
                  (filters.latestScoreRange[0] !== 0 ||
                    filters.latestScoreRange[1] !== 100) &&
                    "Latest Score",
                  (filters.improvementRange[0] !== -100 ||
                    filters.improvementRange[1] !== 100) &&
                    "Improvement",
                  (filters.interviewCountRange[0] !== 0 ||
                    filters.interviewCountRange[1] !== 1000) &&
                    "Interview Count",
                  filters.smartFilters.length > 0 &&
                    `${filters.smartFilters.length} Smart`,
                ]
                  .filter(Boolean)
                  .length}{" "}
                active
              </Badge>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

