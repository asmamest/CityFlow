import { NextResponse } from "next/server"
import { getApiUrl } from "@/lib/api-config"

export async function GET() {
  try {
    const response = await fetch(getApiUrl('/lignes'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // Pour avoir toujours les données fraîches
    })

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Erreur lors de la récupération des lignes:', error)
    return NextResponse.json(
      { error: 'Impossible de récupérer les lignes' },
      { status: 500 }
    )
  }
}