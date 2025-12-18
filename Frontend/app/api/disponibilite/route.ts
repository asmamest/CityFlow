import { NextResponse } from "next/server"

export async function GET() {
  try {
    // Replace with your actual backend URL
    const response = await fetch("http://localhost:8000/disponibilite", { cache: "no-store" })
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching disponibilite:", error)

    // Fallback demo data
    return NextResponse.json({
      timestamp: new Date().toISOString(),
      nombre_lignes: 4,
      disponibilites: [
        {
          ligne_id: "1",
          vehicules_total: 21,
          vehicules_en_service: 18,
          taux_disponibilite: 90,
          derniere_maj: new Date().toISOString(),
        },
        {
          ligne_id: "2",
          vehicules_total: 15,
          vehicules_en_service: 12,
          taux_disponibilite: 80,
          derniere_maj: new Date().toISOString(),
        },
        {
          ligne_id: "3",
          vehicules_total: 10,
          vehicules_en_service: 9,
          taux_disponibilite: 90,
          derniere_maj: new Date().toISOString(),
        },
        {
          ligne_id: "4",
          vehicules_total: 8,
          vehicules_en_service: 7,
          taux_disponibilite: 87.5,
          derniere_maj: new Date().toISOString(),
        },
      ],
    })
  }
}
