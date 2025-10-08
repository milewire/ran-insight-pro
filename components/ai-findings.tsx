"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, AlertTriangle, CheckCircle2, TrendingUp, Brain } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"

interface AIFindingsProps {
  summary?: string
  isLoading?: boolean
}

export function AIFindings({ summary, isLoading = false }: AIFindingsProps) {
  const defaultFindings = [
    {
      icon: AlertTriangle,
      color: "text-yellow-500",
      title: "High PRB Utilization Detected",
      description:
        "Cluster 3 showing 92% PRB utilization during peak hours (18:00-20:00). Consider capacity expansion.",
    },
    {
      icon: CheckCircle2,
      color: "text-green-500",
      title: "SINR Performance Optimal",
      description: "Average SINR levels maintained above 15dB across all clusters, indicating good signal quality.",
    },
    {
      icon: TrendingUp,
      color: "text-cyan-500",
      title: "RTWP Trending Improvement",
      description: "RTWP values improved by 3dB over the past week, suggesting reduced interference levels.",
    },
  ]

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-accent" />
          <CardTitle className="text-2xl font-bold">AI Findings</CardTitle>
        </div>
        <CardDescription className="text-muted-foreground">
          Automated insights and recommendations based on network performance data
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <div className="space-y-3 mt-6">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          </div>
        ) : summary ? (
          <div className="space-y-4">
            <div className="flex gap-4 p-4 rounded-lg bg-primary/5 border border-primary/20">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Brain className="w-5 h-5 text-primary" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-foreground mb-2">AI Analysis Summary</h4>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{summary}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {defaultFindings.map((finding, index) => {
              const Icon = finding.icon
              return (
                <div
                  key={index}
                  className="flex gap-4 p-4 rounded-lg bg-muted/30 border border-border hover:bg-muted/50 transition-colors"
                >
                  <div
                    className={`w-10 h-10 rounded-lg bg-background flex items-center justify-center flex-shrink-0 ${finding.color}`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-foreground mb-1">{finding.title}</h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">{finding.description}</p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
