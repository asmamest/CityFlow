import { NextResponse } from "next/server"

export async function GET(request: Request, { params }: { params: Promise<{ zone: string }> }) {
  const { zone } = await params

  try {
    const response = await fetch(`http://localhost:8000/api/aqi/${zone}`)

    if (!response.ok) {
      throw new Error("Failed to fetch AQI")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching AQI:", error)

    // Fallback demo data
    const aqi = Math.floor(Math.random() * 200)
    let category = "Bon"
    if (aqi > 150) category = "Mauvais"
    else if (aqi > 100) category = "Modéré"
    else if (aqi > 50) category = "Acceptable"

    return NextResponse.json({
      zone,
      aqi,
      category,
      timestamp: new Date().toISOString(),
    })
  }
}
