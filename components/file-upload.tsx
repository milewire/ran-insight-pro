"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, FileText, AlertCircle, CheckCircle2 } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>
  isLoading?: boolean
  error?: string | null
}

export function FileUpload({ onFileUpload, isLoading = false, error = null }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === "text/csv" || file.name.endsWith(".csv")) {
        setSelectedFile(file)
        onFileUpload(file)
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setSelectedFile(file)
      onFileUpload(file)
    }
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-xl font-bold flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Upload KPI Data
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          Upload a CSV file containing RTWP, SINR, and PRB measurements for analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50"
          } ${isLoading ? "opacity-50 pointer-events-none" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            className="hidden"
            disabled={isLoading}
            aria-label="Upload CSV file"
          />
          
          <div className="space-y-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="w-6 h-6 text-primary" />
            </div>
            
            <div>
              <p className="text-lg font-medium text-foreground">
                {selectedFile ? selectedFile.name : "Drop your CSV file here"}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                or click to browse files
              </p>
            </div>
            
            <Button
              onClick={handleButtonClick}
              disabled={isLoading}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {isLoading ? "Processing..." : "Choose File"}
            </Button>
          </div>
        </div>

        {selectedFile && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/30 border border-border">
            <FileText className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-foreground">{selectedFile.name}</span>
            <span className="text-xs text-muted-foreground">
              ({(selectedFile.size / 1024).toFixed(1)} KB)
            </span>
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {selectedFile && !error && !isLoading && (
          <Alert>
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              File uploaded successfully! Analysis results will appear below.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
