import { NextResponse } from "next/server"
import { getApiUrl } from "@/lib/api-config"

export async function GET(
  request: Request,
  { params }: { params: Promise<{ ligne: string }> }
) {
  try {
    const { ligne } = await params

    const response = await fetch(getApiUrl(`/horaires/${ligne}`), {
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
    
    // L'API backend retourne { horaires: [...], ... }
    // On retourne directement le tableau horaires
    return NextResponse.json(data.horaires || [])
  } catch (error) {
    console.error('Erreur lors de la récupération des horaires:', error)
    return NextResponse.json(
      { error: 'Impossible de récupérer les horaires' },
      { status: 500 }
    )
  }
}