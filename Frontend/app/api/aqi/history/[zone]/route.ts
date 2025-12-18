import { NextResponse } from "next/server"

export async function GET(request: Request, { params }: { params: Promise<{ zone: string }> }) {
  const { zone } = await params

  try {
    const response = await fetch(`http://localhost:8002/api/history/${zone}`)

    if (!response.ok) {
      throw new Error("Failed to fetch history")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching history:", error)

    // Fallback demo data
    const history = []
    for (let i = 0; i < 10; i++) {
      const date = new Date()
      date.setHours(date.getHours() - i)
      history.push({
        timestamp: date.toISOString(),
        aqi: Math.floor(Math.random() * 200),
      })
    }

    return NextResponse.json({ history })
  }
}
