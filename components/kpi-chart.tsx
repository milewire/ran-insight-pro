"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Skeleton } from "@/components/ui/skeleton"

// Sample data for PRB, SINR, and RTWP metrics
const defaultKpiData = [
  { time: "00:00", prb: 65, sinr: 18, rtwp: -95 },
  { time: "02:00", prb: 58, sinr: 19, rtwp: -96 },
  { time: "04:00", prb: 52, sinr: 20, rtwp: -97 },
  { time: "06:00", prb: 48, sinr: 21, rtwp: -98 },
  { time: "08:00", prb: 72, sinr: 17, rtwp: -94 },
  { time: "10:00", prb: 78, sinr: 16, rtwp: -93 },
  { time: "12:00", prb: 82, sinr: 15, rtwp: -92 },
  { time: "14:00", prb: 85, sinr: 15, rtwp: -91 },
  { time: "16:00", prb: 88, sinr: 14, rtwp: -90 },
  { time: "18:00", prb: 92, sinr: 13, rtwp: -89 },
  { time: "20:00", prb: 87, sinr: 14, rtwp: -91 },
  { time: "22:00", prb: 75, sinr: 16, rtwp: -93 },
]

interface KPIChartProps {
  data?: Array<{
    time: string
    prb: number
    sinr: number
    rtwp: number
  }>
  isLoading?: boolean
}

export function KPIChart({ data = defaultKpiData, isLoading = false }: KPIChartProps) {
  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">KPI Metrics Timeline</CardTitle>
        <CardDescription className="text-muted-foreground">
          PRB Utilization, SINR, and RTWP measurements over 24 hours
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[400px] space-y-4">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-[300px] w-full" />
          </div>
        ) : (
          <ChartContainer
            config={{
              prb: {
                label: "PRB Utilization (%)",
                color: "hsl(var(--chart-1))",
              },
              sinr: {
                label: "SINR (dB)",
                color: "hsl(var(--chart-2))",
              },
              rtwp: {
                label: "RTWP (dBm)",
                color: "hsl(var(--chart-3))",
              },
            }}
            className="h-[400px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                <XAxis
                  dataKey="time"
                  stroke="hsl(var(--muted-foreground))"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <YAxis stroke="hsl(var(--muted-foreground))" tick={{ fill: "hsl(var(--muted-foreground))" }} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend
                  wrapperStyle={{
                    paddingTop: "20px",
                    color: "hsl(var(--foreground))",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="prb"
                  stroke="var(--color-prb)"
                  strokeWidth={2.5}
                  name="PRB Utilization (%)"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="sinr"
                  stroke="var(--color-sinr)"
                  strokeWidth={2.5}
                  name="SINR (dB)"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="rtwp"
                  stroke="var(--color-rtwp)"
                  strokeWidth={2.5}
                  name="RTWP (dBm)"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
