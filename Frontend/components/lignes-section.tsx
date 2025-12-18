"use client"

import { useEffect, useState } from "react"
import { RefreshCw, Bus, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface Ligne {
  numero: string
  nom: string
  type_transport: string
  terminus_debut: string
  terminus_fin: string
  actif: boolean
}

export function LignesSection() {
  const [lignes, setLignes] = useState<Ligne[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLignes = async () => {
    setLoading(true)
    setError(null)
    try {
      // Replace with your actual API endpoint
      const response = await fetch("/api/lignes")
      if (!response.ok) throw new Error("Erreur de chargement des lignes")
      const data = await response.json()
      setLignes(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLignes()
  }, [])

  const getTransportIcon = (type: string) => {
    return type.toLowerCase().includes("bus") ? Bus : Zap
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Lignes de transport</h2>
          <p className="text-muted-foreground mt-1">Consultez toutes les lignes disponibles</p>
        </div>
        <Button onClick={fetchLignes} disabled={loading} variant="outline" size="sm">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Actualiser
        </Button>
      </div>

      {error && (
        <Card className="p-4 bg-destructive/10 border-destructive/20">
          <p className="text-destructive text-sm">{error}</p>
        </Card>
      )}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="p-6 animate-pulse">
              <div className="h-6 bg-muted rounded mb-4" />
              <div className="h-4 bg-muted rounded mb-2" />
              <div className="h-4 bg-muted rounded w-2/3" />
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {lignes.map((ligne) => {
            const Icon = getTransportIcon(ligne.type_transport)
            return (
              <Card key={ligne.numero} className="p-6 hover:shadow-lg transition-shadow duration-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <Icon className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-foreground">{ligne.numero}</div>
                      <div className="text-xs text-muted-foreground">{ligne.type_transport}</div>
                    </div>
                  </div>
                  <div
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      ligne.actif ? "bg-success/10 text-success" : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {ligne.actif ? "Actif" : "Inactif"}
                  </div>
                </div>

                <h3 className="font-semibold text-foreground mb-3">{ligne.nom}</h3>

                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="h-2 w-2 rounded-full bg-primary" />
                    <span>{ligne.terminus_debut}</span>
                  </div>
                  <div className="ml-1 border-l-2 border-dashed border-border h-4" />
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="h-2 w-2 rounded-full bg-primary" />
                    <span>{ligne.terminus_fin}</span>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      {!loading && lignes.length === 0 && !error && (
        <Card className="p-12 text-center">
          <Bus className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Aucune ligne disponible</p>
        </Card>
      )}
    </div>
  )
}
