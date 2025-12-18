"use client"

import { useEffect, useState } from "react"
import { RefreshCw, AlertCircle, CheckCircle, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface Trafic {
  ligne_id: string
  statut: string
  retard_minutes: number
  message: string
  timestamp: string
}

export function TraficSection() {
  const [trafic, setTrafic] = useState<Trafic[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTrafic = async () => {
    setLoading(true)
    setError(null)
    try {
      // Replace with your actual API endpoint
      const response = await fetch("/api/trafic")
      if (!response.ok) throw new Error("Erreur de chargement du trafic")
      const data = await response.json()
      setTrafic(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTrafic()
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchTrafic, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (statut: string, retard: number) => {
    const statusLower = statut.toLowerCase()
    if (statusLower.includes("normal") || retard === 0) {
      return {
        bg: "bg-success/10",
        border: "border-success/20",
        text: "text-success",
        icon: CheckCircle,
      }
    } else if (retard < 10) {
      return {
        bg: "bg-warning/10",
        border: "border-warning/20",
        text: "text-warning",
        icon: Clock,
      }
    } else {
      return {
        bg: "bg-destructive/10",
        border: "border-destructive/20",
        text: "text-destructive",
        icon: AlertCircle,
      }
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">État du trafic</h2>
          <p className="text-muted-foreground mt-1">Informations en temps réel sur toutes les lignes</p>
        </div>
        <Button onClick={fetchTrafic} disabled={loading} variant="outline" size="sm">
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
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <Card key={i} className="p-5 animate-pulse">
              <div className="h-6 bg-muted rounded mb-2" />
              <div className="h-4 bg-muted rounded w-3/4" />
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {trafic.map((item) => {
            const status = getStatusColor(item.statut, item.retard_minutes)
            const Icon = status.icon

            return (
              <Card
                key={item.ligne_id}
                className={`p-5 border ${status.border} ${status.bg} hover:shadow-md transition-shadow duration-200`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-4 flex-1">
                    <div className={`p-3 rounded-lg ${status.bg}`}>
                      <Icon className={`h-5 w-5 ${status.text}`} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg text-foreground">Ligne {item.ligne_id}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${status.bg} ${status.text}`}>
                          {item.statut}
                        </span>
                      </div>

                      <p className="text-sm text-muted-foreground mb-2">{item.message}</p>

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        {item.retard_minutes > 0 && (
                          <span className={status.text}>Retard: {item.retard_minutes} min</span>
                        )}
                        <span>Mis à jour: {new Date(item.timestamp).toLocaleTimeString("fr-FR")}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      {!loading && trafic.length === 0 && !error && (
        <Card className="p-12 text-center">
          <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Aucune information de trafic disponible</p>
        </Card>
      )}
    </div>
  )
}
