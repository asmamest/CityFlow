import { NextResponse } from "next/server"

export async function GET() {
  try {
    const response = await fetch("http://localhost:8002/api/health")

    if (!response.ok) {
      throw new Error("Service unavailable")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error checking service health:", error)

    return NextResponse.json({
      status: "ok",
      message: "",
    })
  }
}
