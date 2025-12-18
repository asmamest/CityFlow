import { NextResponse } from "next/server"

export async function GET(request: Request, { params }: { params: Promise<{ zoneA: string; zoneB: string }> }) {
  const { zoneA, zoneB } = await params

  try {
    const response = await fetch(`http://localhost:8002/api/compare/${zoneA}/${zoneB}`)

    if (!response.ok) {
      throw new Error("Failed to compare zones")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error comparing zones:", error)

    // Fallback demo data
    const aqiA = Math.floor(Math.random() * 200)
    const aqiB = Math.floor(Math.random() * 200)

    return NextResponse.json({
      zoneA,
      zoneB,
      aqiA,
      aqiB,
      difference: aqiA - aqiB,
    })
  }
}
