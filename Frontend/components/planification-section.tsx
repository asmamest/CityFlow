/**
 * Exemple d'intégration de la fonction de planification dans le composant PlanificationSection
 * Modifiez votre fichier planification-section.tsx
 */

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { MapPin, Navigation, Clock, Route } from "lucide-react"
// Importez votre fonction de planification
import { planifierItineraire } from "@/lib/route-planner"

interface ItineraireSegment {
  ligne: string
  depart: string
  arrivee: string
  duree_minutes: number
  type: string
}

interface Itineraire {
  itineraire_id: number
  depart: string
  arrivee: string
  duree_totale_minutes: number
  nombre_correspondances: number
  heure_depart: string
  heure_arrivee: string
  segments: ItineraireSegment[]
}

export function PlanificationSection() {
  const [depart, setDepart] = useState("")
  const [arrivee, setArrivee] = useState("")
  const [heureDepart, setHeureDepart] = useState("")
  const [itineraires, setItineraires] = useState<Itineraire[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fonction modifiée pour utiliser la planification côté frontend
  const planifierTrajet = async () => {
    if (!depart || !arrivee) {
      alert("Veuillez renseigner le départ et l'arrivée")
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      // OPTION 1: Appel direct côté frontend (recommandé)
      const result = await planifierItineraire(
        depart,
        arrivee,
        heureDepart || undefined,
        "http://localhost:8000" // URL de votre backend
      )
      
      setItineraires(result.itineraires || [])
      
      if (result.itineraires.length === 0) {
        setError("Aucun itinéraire trouvé entre ces stations.")
      }
    } catch (error) {
      console.error("Erreur lors de la planification:", error)
      setError("Une erreur est survenue lors de la recherche d'itinéraires.")
      setItineraires([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground">Planification de Trajet</h2>
        <p className="text-muted-foreground mt-2">Trouvez le meilleur itinéraire pour votre trajet</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Rechercher un itinéraire</CardTitle>
          <CardDescription>Entrez votre point de départ et votre destination</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="depart">
                <MapPin className="h-4 w-4 inline mr-2" />
                Départ
              </Label>
              <Input
                id="depart"
                placeholder="Ex: Gare Centrale"
                value={depart}
                onChange={(e) => setDepart(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="arrivee">
                <Navigation className="h-4 w-4 inline mr-2" />
                Arrivée
              </Label>
              <Input
                id="arrivee"
                placeholder="Ex: Banlieue Nord"
                value={arrivee}
                onChange={(e) => setArrivee(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="heure">
                <Clock className="h-4 w-4 inline mr-2" />
                Heure de départ (optionnel)
              </Label>
              <Input id="heure" type="time" value={heureDepart} onChange={(e) => setHeureDepart(e.target.value)} />
            </div>
          </div>
          <Button onClick={planifierTrajet} disabled={loading} className="w-full md:w-auto">
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Recherche en cours...
              </>
            ) : (
              <>
                <Route className="h-4 w-4 mr-2" />
                Planifier mon trajet
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-2 border-destructive/50">
          <CardContent className="flex items-center justify-center py-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {itineraires.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">Itinéraires disponibles ({itineraires.length})</h3>
          {itineraires.map((itineraire) => (
            <Card key={itineraire.itineraire_id} className="border-2 hover:border-primary transition-colors">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">
                      {itineraire.depart} → {itineraire.arrivee}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {itineraire.nombre_correspondances === 0
                        ? "Direct"
                        : `${itineraire.nombre_correspondances} correspondance${
                            itineraire.nombre_correspondances > 1 ? "s" : ""
                          }`}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">{itineraire.duree_totale_minutes} min</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {itineraire.heure_depart} - {itineraire.heure_arrivee}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {itineraire.segments.map((segment, index) => (
                    <div key={index} className="flex items-center gap-4">
                      <div className="flex-shrink-0 w-16 h-8 bg-primary rounded flex items-center justify-center">
                        <span className="text-sm font-bold text-primary-foreground">{segment.ligne}</span>
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">
                          {segment.depart} → {segment.arrivee}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {segment.duree_minutes} min • {segment.type}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && itineraires.length === 0 && depart && arrivee && !error && (
        <Card className="border-2 border-dashed">
          <CardContent className="flex items-center justify-center py-12">
            <p className="text-muted-foreground">Aucun itinéraire trouvé. Essayez avec d'autres stations.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}