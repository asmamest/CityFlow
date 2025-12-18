import { NextResponse } from "next/server"
import { URL } from "url"

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const depart = searchParams.get("depart")
    const arrivee = searchParams.get("arrivee")
    const heureDepart = searchParams.get("heure_depart")

    if (!depart || !arrivee) {
      return NextResponse.json({ error: "Départ et arrivée requis" }, { status: 400 })
    }

    // Build query params for backend
    const backendParams = new URLSearchParams({
      depart,
      arrivee,
      ...(heureDepart && { heure_depart: heureDepart }),
    })

    // Replace with your actual backend URL
    const response = await fetch(`http://localhost:8000/planification?${backendParams}`)
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching planification:", error)

    // Fallback demo data
    return NextResponse.json({
      timestamp: new Date().toISOString(),
      nombre_itineraires: 2,
      itineraires: [
        {
          itineraire_id: 1,
          depart: "Station A",
          arrivee: "Station B",
          duree_totale_minutes: 25,
          nombre_correspondances: 0,
          heure_depart: "14:00",
          heure_arrivee: "14:25",
          segments: [
            {
              ligne: "1",
              depart: "Station A",
              arrivee: "Station B",
              duree_minutes: 25,
              type: "Bus",
            },
          ],
        },
        {
          itineraire_id: 2,
          depart: "Station A",
          arrivee: "Station B",
          duree_totale_minutes: 30,
          nombre_correspondances: 1,
          heure_depart: "14:05",
          heure_arrivee: "14:35",
          segments: [
            {
              ligne: "2",
              depart: "Station A",
              arrivee: "Station C",
              duree_minutes: 15,
              type: "Bus",
            },
            {
              ligne: "3",
              depart: "Station C",
              arrivee: "Station B",
              duree_minutes: 15,
              type: "Métro",
            },
          ],
        },
      ],
    })
  }
}
