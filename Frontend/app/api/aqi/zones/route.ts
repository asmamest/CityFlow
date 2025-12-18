import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Connect to backend REST API
    const response = await fetch("http://localhost:8002/api/zones")

    if (!response.ok) {
      throw new Error("Failed to fetch zones")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching zones:", error)

    // Fallback demo data
    return NextResponse.json({
      zones: ["Paris Centre", "Bordeaux", "Lyon", "Marseille", "Toulouse"],
    })
  }
}
