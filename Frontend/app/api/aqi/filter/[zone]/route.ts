import { NextResponse } from "next/server"

export async function GET(request: Request, { params }: { params: Promise<{ zone: string }> }) {
  const { zone } = await params
  const { searchParams } = new URL(request.url)
  const threshold = searchParams.get("threshold")

  try {
    const response = await fetch(`http://localhost:8002/api/filter/${zone}?threshold=${threshold}`)

    if (!response.ok) {
      throw new Error("Failed to filter pollutants")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error filtering pollutants:", error)

    // Fallback demo data
    const allPollutants = [
      { name: "PM2.5", value: 65, unit: "μg/m³" },
      { name: "PM10", value: 120, unit: "μg/m³" },
      { name: "NO2", value: 45, unit: "μg/m³" },
      { name: "O3", value: 95, unit: "μg/m³" },
    ]

    const filtered = allPollutants.filter((p) => p.value >= Number(threshold || 0))

    return NextResponse.json({ pollutants: filtered })
  }
}
