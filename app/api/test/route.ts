import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'success',
    message: 'RAN Insight Pro API is working!',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV
  })
}
