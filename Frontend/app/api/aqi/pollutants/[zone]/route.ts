import { NextResponse } from "next/server"

export async function GET(request: Request, { params }: { params: Promise<{ zone: string }> }) {
  const { zone } = await params

  try {
    const response = await fetch(`http://localhost:8000/api/pollutants/${zone}`)

    if (!response.ok) {
      throw new Error("Failed to fetch pollutants")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching pollutants:", error)

    // Fallback demo data
    return NextResponse.json({
      pollutants: [
        { name: "PM2.5", value: Math.floor(Math.random() * 100), unit: "μg/m³", status: "Normal" },
        { name: "PM10", value: Math.floor(Math.random() * 150), unit: "μg/m³", status: "Normal" },
        { name: "NO2", value: Math.floor(Math.random() * 80), unit: "μg/m³", status: "Normal" },
        { name: "O3", value: Math.floor(Math.random() * 120), unit: "μg/m³", status: "Modéré" },
        { name: "CO", value: Math.floor(Math.random() * 50), unit: "mg/m³", status: "Bon" },
        { name: "SO2", value: Math.floor(Math.random() * 60), unit: "μg/m³", status: "Normal" },
      ],
    })
  }
}
