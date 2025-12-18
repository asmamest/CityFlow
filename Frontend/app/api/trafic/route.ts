import { NextResponse } from "next/server"
import { getApiUrl } from "@/lib/api-config"

export async function GET() {
  try {
    const response = await fetch(getApiUrl('/trafic'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      throw new Error(`Erreur API: ${response.status}`)
    }

    const data = await response.json()
    
    // L'API backend retourne { trafic: [...], ... }
    // On retourne directement le tableau trafic
    return NextResponse.json(data.trafic || [])
  } catch (error) {
    console.error('Erreur lors de la récupération du trafic:', error)
    return NextResponse.json(
      { error: 'Impossible de récupérer l\'état du trafic' },
      { status: 500 }
    )
  }
}