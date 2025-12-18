"use client"

import { useEffect, useState } from "react"
import { RefreshCw, Calendar, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface Horaire {
  id: string
  ligne_id: string
  destination: string
  heure_depart: string
  heure_arrivee: string
  station: string
  quai: string
}

interface Ligne {
  id: string
  numero: string
  nom: string
  type_transport: string
  terminus_debut: string
  terminus_fin: string
  actif: boolean
}

export function HorairesSection() {
  const [lignes, setLignes] = useState<Ligne[]>([])
  const [selectedLigne, setSelectedLigne] = useState<string>("")
  const [horaires, setHoraires] = useState<Horaire[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingLignes, setLoadingLignes] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Charger la liste des lignes au montage du composant
  useEffect(() => {
    const fetchLignes = async () => {
      setLoadingLignes(true)
      try {
        const response = await fetch('/api/lignes')
        if (!response.ok) throw new Error("Erreur de chargement des lignes")
        const data = await response.json()
        
        // Filtrer uniquement les lignes actives
        const lignesActives = data.filter((ligne: Ligne) => ligne.actif)
        setLignes(lignesActives)
        
        // Sélectionner automatiquement la première ligne
        if (lignesActives.length > 0) {
          setSelectedLigne(lignesActives[0].numero)
        }
      } catch (err) {
        console.error("Erreur:", err)
        setError("Impossible de charger les lignes")
      } finally {
        setLoadingLignes(false)
      }
    }

    fetchLignes()
  }, [])

  // Charger les horaires quand la ligne change
  useEffect(() => {
    if (selectedLigne) {
      fetchHoraires(selectedLigne)
    }
  }, [selectedLigne])

  const fetchHoraires = async (ligne: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/horaires/${ligne}`)
      if (!response.ok) throw new Error("Erreur de chargement des horaires")
      const data = await response.json()
      setHoraires(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Horaires</h2>
          <p className="text-muted-foreground mt-1">Consultez les horaires de passage</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedLigne}
            onChange={(e) => setSelectedLigne(e.target.value)}
            disabled={loadingLignes || lignes.length === 0}
            className="px-4 py-2 rounded-lg border border-input bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loadingLignes ? (
              <option value="">Chargement...</option>
            ) : lignes.length === 0 ? (
              <option value="">Aucune ligne disponible</option>
            ) : (
              lignes.map((ligne) => (
                <option key={ligne.id} value={ligne.numero}>
                  Ligne {ligne.numero} - {ligne.nom}
                </option>
              ))
            )}
          </select>
          <Button 
            onClick={() => selectedLigne && fetchHoraires(selectedLigne)} 
            disabled={loading || !selectedLigne} 
            variant="outline" 
            size="sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {error && (
        <Card className="p-4 bg-destructive/10 border-destructive/20">
          <p className="text-destructive text-sm">{error}</p>
        </Card>
      )}

      {loading ? (
        <Card className="overflow-hidden">
          <div className="animate-pulse">
            <div className="h-12 bg-muted" />
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-16 bg-background border-t border-border" />
            ))}
          </div>
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Destination</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Départ</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Arrivée</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Station</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">Quai</th>
                </tr>
              </thead>
              <tbody>
                {horaires.map((horaire, index) => (
                  <tr
                    key={horaire.id}
                    className={`border-b border-border hover:bg-accent/50 transition-colors ${
                      index % 2 === 0 ? "bg-background" : "bg-muted/20"
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-primary" />
                        <span className="font-medium text-foreground">{horaire.destination}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>{horaire.heure_depart}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground">{horaire.heure_arrivee}</td>
                    <td className="px-6 py-4 text-foreground">{horaire.station}</td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                        Quai {horaire.quai}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {!loading && horaires.length === 0 && !error && selectedLigne && (
        <Card className="p-12 text-center">
          <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Aucun horaire disponible pour la ligne {selectedLigne}</p>
        </Card>
      )}
    </div>
  )
}