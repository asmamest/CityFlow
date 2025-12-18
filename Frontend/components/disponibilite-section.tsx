"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bus, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Disponibilite {
  ligne_id: string
  vehicules_total: number
  vehicules_en_service: number
  taux_disponibilite: number
  derniere_maj: string
}

interface DisponibiliteResponse {
  timestamp: string
  nombre_lignes: number
  disponibilites: Disponibilite[]
}

export function DisponibiliteSection() {
  const [data, setData] = useState<DisponibiliteResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchDisponibilite = async () => {
    setLoading(true)
    try {
      const response = await fetch("/api/disponibilite")
      const result = await response.json()
      setData(result)
    } catch (error) {
      console.error("Erreur lors du chargement des disponibilités:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDisponibilite()
    const interval = setInterval(fetchDisponibilite, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getTauxColor = (taux: number) => {
    if (taux >= 85) return "text-success"
    if (taux >= 70) return "text-warning"
    return "text-danger"
  }

  const getTauxBg = (taux: number) => {
    if (taux >= 85) return "bg-success/10 border-success/20"
    if (taux >= 70) return "bg-warning/10 border-warning/20"
    return "bg-danger/10 border-danger/20"
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Disponibilité des Véhicules</h2>
          <p className="text-muted-foreground mt-2">Suivi en temps réel de la disponibilité des véhicules par ligne</p>
        </div>
        <Button onClick={fetchDisponibilite} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {data && (
        <div className="text-sm text-muted-foreground">
          Dernière mise à jour: {new Date(data.timestamp).toLocaleString("fr-FR")}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {data?.disponibilites.map((dispo) => (
          <Card key={dispo.ligne_id} className={`border-2 ${getTauxBg(dispo.taux_disponibilite)}`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bus className="h-5 w-5" />
                  Ligne {dispo.ligne_id}
                </CardTitle>
                <div className={`text-2xl font-bold ${getTauxColor(dispo.taux_disponibilite)}`}>
                  {dispo.taux_disponibilite.toFixed(1)}%
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total véhicules:</span>
                <span className="font-medium">{dispo.vehicules_total}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">En service:</span>
                <span className="font-medium text-success">{dispo.vehicules_en_service}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Hors service:</span>
                <span className="font-medium text-danger">{dispo.vehicules_total - dispo.vehicules_en_service}</span>
              </div>
              <div className="pt-2 border-t border-border/50">
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      dispo.taux_disponibilite >= 85
                        ? "bg-success"
                        : dispo.taux_disponibilite >= 70
                          ? "bg-warning"
                          : "bg-danger"
                    }`}
                    style={{ width: `${dispo.taux_disponibilite}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
