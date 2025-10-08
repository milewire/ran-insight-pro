import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'

export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      return NextResponse.json({ error: 'Only CSV files are supported' }, { status: 400 })
    }

    // Process the file (enhanced version with better error handling)
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())
    
    if (lines.length < 2) {
      return NextResponse.json({ error: 'CSV file must have at least a header and one data row' }, { status: 400 })
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
    
    // Parse CSV data with better error handling
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

    if (data.length === 0) {
      return NextResponse.json({ error: 'No valid data found. Please ensure your CSV contains RTWP, SINR, or PRB columns.' }, { status: 400 })
    }

    // Generate comprehensive AI summary
    const rtwpData = data.filter(d => d.rtwp !== undefined)
    const sinrData = data.filter(d => d.sinr !== undefined)
    const prbData = data.filter(d => d.prb !== undefined)

    const summary = `RAN Analysis Complete for ${file.name}

📊 Data Summary:
- Total data points: ${data.length}
- RTWP measurements: ${rtwpData.length}
- SINR measurements: ${sinrData.length}
- PRB utilization: ${prbData.length}

🔍 Key Insights:
- Average RTWP: ${rtwpData.length > 0 ? (rtwpData.reduce((sum, d) => sum + d.rtwp, 0) / rtwpData.length).toFixed(2) : 'N/A'} dBm
- Average SINR: ${sinrData.length > 0 ? (sinrData.reduce((sum, d) => sum + d.sinr, 0) / sinrData.length).toFixed(2) : 'N/A'} dB
- Average PRB: ${prbData.length > 0 ? (prbData.reduce((sum, d) => sum + d.prb, 0) / prbData.length).toFixed(2) : 'N/A'}%

📈 Network Performance:
${rtwpData.length > 0 ? `- RTWP range: ${Math.min(...rtwpData.map(d => d.rtwp)).toFixed(2)} to ${Math.max(...rtwpData.map(d => d.rtwp)).toFixed(2)} dBm` : ''}
${sinrData.length > 0 ? `- SINR range: ${Math.min(...sinrData.map(d => d.sinr)).toFixed(2)} to ${Math.max(...sinrData.map(d => d.sinr)).toFixed(2)} dB` : ''}
${prbData.length > 0 ? `- PRB range: ${Math.min(...prbData.map(d => d.prb)).toFixed(2)} to ${Math.max(...prbData.map(d => d.prb)).toFixed(2)}%` : ''}

✅ Analysis completed successfully at ${new Date().toLocaleString()}`

    return NextResponse.json({
      summary,
      data,
      filename: file.name,
      processed_at: new Date().toISOString(),
      user_id: userId,
      metrics: {
        total_points: data.length,
        rtwp_points: rtwpData.length,
        sinr_points: sinrData.length,
        prb_points: prbData.length
      }
    })

  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { error: 'Failed to analyze file. Please ensure it\'s a valid CSV with RAN data.' }, 
      { status: 500 }
    )
  }
}
