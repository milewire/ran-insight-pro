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

    // Calculate statistics
    const avgRtwp = rtwpData.length > 0 ? rtwpData.reduce((sum, d) => sum + d.rtwp, 0) / rtwpData.length : 0
    const avgSinr = sinrData.length > 0 ? sinrData.reduce((sum, d) => sum + d.sinr, 0) / sinrData.length : 0
    const avgPrb = prbData.length > 0 ? prbData.reduce((sum, d) => sum + d.prb, 0) / prbData.length : 0

    const minRtwp = rtwpData.length > 0 ? Math.min(...rtwpData.map(d => d.rtwp)) : 0
    const maxRtwp = rtwpData.length > 0 ? Math.max(...rtwpData.map(d => d.rtwp)) : 0
    const minSinr = sinrData.length > 0 ? Math.min(...sinrData.map(d => d.sinr)) : 0
    const maxSinr = sinrData.length > 0 ? Math.max(...sinrData.map(d => d.sinr)) : 0
    const minPrb = prbData.length > 0 ? Math.min(...prbData.map(d => d.prb)) : 0
    const maxPrb = prbData.length > 0 ? Math.max(...prbData.map(d => d.prb)) : 0

    // Try to generate AI summary with OpenAI
    let aiSummary = ''
    try {
      const openaiApiKey = process.env.OPENAI_API_KEY
      if (openaiApiKey) {
        const openai = await import('openai')
        const client = new openai.OpenAI({
          apiKey: openaiApiKey,
        })

        const prompt = `Analyze this RAN (Radio Access Network) data and provide professional insights:

File: ${file.name}
Data Points: ${data.length}
RTWP Measurements: ${rtwpData.length} (Avg: ${avgRtwp.toFixed(2)} dBm, Range: ${minRtwp.toFixed(2)}-${maxRtwp.toFixed(2)} dBm)
SINR Measurements: ${sinrData.length} (Avg: ${avgSinr.toFixed(2)} dB, Range: ${minSinr.toFixed(2)}-${maxSinr.toFixed(2)} dB)
PRB Utilization: ${prbData.length} (Avg: ${avgPrb.toFixed(2)}%, Range: ${minPrb.toFixed(2)}-${maxPrb.toFixed(2)}%)

Please provide:
1. Network performance assessment
2. Potential issues or anomalies
3. Recommendations for optimization
4. Overall health score (1-10)

Keep response concise and professional.`

        const completion = await client.chat.completions.create({
          model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: parseInt(process.env.OPENAI_MAX_TOKENS || '1000'),
          temperature: 0.7,
        })

        aiSummary = completion.choices[0]?.message?.content || ''
      }
    } catch (error) {
      console.error('OpenAI API error:', error)
      // Fallback to basic summary if OpenAI fails
    }

    // Fallback summary if no AI analysis
    if (!aiSummary) {
      aiSummary = `RAN Analysis Complete for ${file.name}

📊 Data Summary:
- Total data points: ${data.length}
- RTWP measurements: ${rtwpData.length}
- SINR measurements: ${sinrData.length}
- PRB utilization: ${prbData.length}

🔍 Key Insights:
- Average RTWP: ${rtwpData.length > 0 ? avgRtwp.toFixed(2) : 'N/A'} dBm
- Average SINR: ${sinrData.length > 0 ? avgSinr.toFixed(2) : 'N/A'} dB
- Average PRB: ${prbData.length > 0 ? avgPrb.toFixed(2) : 'N/A'}%

📈 Network Performance:
${rtwpData.length > 0 ? `- RTWP range: ${minRtwp.toFixed(2)} to ${maxRtwp.toFixed(2)} dBm` : ''}
${sinrData.length > 0 ? `- SINR range: ${minSinr.toFixed(2)} to ${maxSinr.toFixed(2)} dB` : ''}
${prbData.length > 0 ? `- PRB range: ${minPrb.toFixed(2)} to ${maxPrb.toFixed(2)}%` : ''}

✅ Analysis completed successfully at ${new Date().toLocaleString()}`
    }

    return NextResponse.json({
      summary: aiSummary,
      data,
      filename: file.name,
      processed_at: new Date().toISOString(),
      user_id: userId,
      metrics: {
        total_points: data.length,
        rtwp_points: rtwpData.length,
        sinr_points: sinrData.length,
        prb_points: prbData.length,
        avg_rtwp: avgRtwp,
        avg_sinr: avgSinr,
        avg_prb: avgPrb
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
