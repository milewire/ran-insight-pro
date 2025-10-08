"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Upload, Activity, TrendingUp, Zap, User, LogOut } from "lucide-react"
import { KPIChart } from "@/components/kpi-chart"
import { AIFindings } from "@/components/ai-findings"
import { FileUpload } from "@/components/file-upload"
import { useUser, useClerk } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import axios from "axios"

export default function RANInsightPro() {
  const { user, isLoaded } = useUser()
  const { signOut } = useClerk()
  const router = useRouter()
  const [cluster, setCluster] = useState("all")
  const [metric, setMetric] = useState("all")
  const [kpiData, setKpiData] = useState<Array<{time: string, prb: number, sinr: number, rtwp: number}>>([])
  const [aiSummary, setAiSummary] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSignOut = async () => {
    await signOut()
    router.push("/")
  }

  const handleFileUpload = async (file: File) => {
    setIsLoading(true)
    setError(null)
    setAiSummary("")
    
    try {
      const formData = new FormData()
      formData.append("file", file)
      
      const response = await axios.post("http://localhost:8000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      
      setAiSummary(response.data.summary)
      
      // Parse CSV data for chart display
      const text = await file.text()
      const lines = text.split('\n').filter(line => line.trim())
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
      
      const data = lines.slice(1).map((line, index) => {
        const values = line.split(',').map(v => v.trim())
        const row: any = { time: `${index * 2}:00` }
        
        headers.forEach((header, i) => {
          if (header.includes('rtwp')) row.rtwp = parseFloat(values[i]) || 0
          if (header.includes('sinr')) row.sinr = parseFloat(values[i]) || 0
          if (header.includes('prb')) row.prb = parseFloat(values[i]) || 0
        })
        
        return row
      }).filter(row => row.rtwp !== undefined || row.sinr !== undefined || row.prb !== undefined)
      
      setKpiData(data)
    } catch (err) {
      setError("Failed to analyze file. Please ensure it's a valid CSV with RTWP, SINR, and PRB columns.")
      console.error("Upload error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      <div className="flex h-screen">
        {/* Left Sidebar */}
        <motion.aside
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="w-72 border-r border-border bg-sidebar p-6 flex flex-col gap-6"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-sidebar-foreground">RAN Insight Pro</h1>
              <p className="text-xs text-muted-foreground">Network Analytics</p>
            </div>
          </div>

          <div className="flex flex-col gap-6 flex-1">
            <div className="space-y-3">
              <Label htmlFor="cluster" className="text-sm font-semibold text-sidebar-foreground">
                Cluster
              </Label>
              <Select value={cluster} onValueChange={setCluster}>
                <SelectTrigger id="cluster" className="bg-sidebar-accent border-sidebar-border">
                  <SelectValue placeholder="Select cluster" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Clusters</SelectItem>
                  <SelectItem value="cluster-1">Cluster 1</SelectItem>
                  <SelectItem value="cluster-2">Cluster 2</SelectItem>
                  <SelectItem value="cluster-3">Cluster 3</SelectItem>
                  <SelectItem value="cluster-4">Cluster 4</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-3">
              <Label htmlFor="metric" className="text-sm font-semibold text-sidebar-foreground">
                Metric
              </Label>
              <Select value={metric} onValueChange={setMetric}>
                <SelectTrigger id="metric" className="bg-sidebar-accent border-sidebar-border">
                  <SelectValue placeholder="Select metric" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Metrics</SelectItem>
                  <SelectItem value="prb">PRB Utilization</SelectItem>
                  <SelectItem value="sinr">SINR</SelectItem>
                  <SelectItem value="rtwp">RTWP</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-4">
              <FileUpload 
                onFileUpload={handleFileUpload}
                isLoading={isLoading}
                error={error}
              />
            </div>

            <div className="pt-6 border-t border-sidebar-border space-y-4">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-sidebar-accent/50">
                <div className="w-8 h-8 rounded-md bg-chart-1/20 flex items-center justify-center">
                  <TrendingUp className="w-4 h-4 text-chart-1" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Active Sites</p>
                  <p className="text-lg font-bold text-sidebar-foreground">1,247</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-sidebar-accent/50">
                <div className="w-8 h-8 rounded-md bg-accent/20 flex items-center justify-center">
                  <Zap className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Alerts</p>
                  <p className="text-lg font-bold text-sidebar-foreground">23</p>
                </div>
              </div>
            </div>

            {/* User Profile Section */}
            {isLoaded && user && (
              <div className="pt-6 border-t border-sidebar-border">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-sidebar-accent/50">
                  <div className="w-8 h-8 rounded-md bg-primary/20 flex items-center justify-center">
                    <User className="w-4 h-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-sidebar-foreground truncate">
                      {user.firstName || user.username || user.emailAddresses[0]?.emailAddress}
                    </p>
                    <p className="text-xs text-muted-foreground truncate">
                      {user.emailAddresses[0]?.emailAddress}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleSignOut}
                    className="h-8 w-8 p-0 hover:bg-destructive/10"
                  >
                    <LogOut className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            )}

            {isLoaded && !user && (
              <div className="pt-6 border-t border-sidebar-border">
                <div className="space-y-2">
                  <Button 
                    onClick={() => router.push("/sign-in")}
                    className="w-full bg-primary hover:bg-primary/90"
                  >
                    Sign In
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => router.push("/sign-up")}
                    className="w-full"
                  >
                    Sign Up
                  </Button>
                </div>
              </div>
            )}
          </div>
        </motion.aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-8 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <h2 className="text-3xl font-bold text-balance mb-2">Network Performance Overview</h2>
              <p className="text-muted-foreground">Real-time KPI monitoring and AI-powered insights</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <KPIChart 
                data={kpiData.length > 0 ? kpiData : undefined}
                isLoading={isLoading}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <AIFindings 
                summary={aiSummary}
                isLoading={isLoading}
              />
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  )
}
