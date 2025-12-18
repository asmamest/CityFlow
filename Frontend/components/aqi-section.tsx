"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Wind, Activity, TrendingUp, Filter, CheckCircle2, AlertCircle } from "lucide-react"

interface AqiData {
  zone: string
  aqi: number
  category: string
  timestamp: string
}

interface Pollutant {
  name: string
  value: number
  unit: string
  status: string
}

interface ComparisonData {
  zoneA: string
  zoneB: string
  aqiA: number
  aqiB: number
  difference: number
}

interface HistoryPoint {
  timestamp: string
  aqi: number
}

export function AqiSection() {
  const [zones, setZones] = useState<string[]>([])
  const [selectedZone, setSelectedZone] = useState("")
  const [aqiData, setAqiData] = useState<AqiData | null>(null)
  const [pollutants, setPollutants] = useState<Pollutant[]>([])
  const [history, setHistory] = useState<HistoryPoint[]>([])
  const [serviceHealth, setServiceHealth] = useState<{ status: string; message: string } | null>(null)

  // Comparison states
  const [zoneA, setZoneA] = useState("")
  const [zoneB, setZoneB] = useState("")
  const [comparison, setComparison] = useState<ComparisonData | null>(null)

  // Filter state
  const [threshold, setThreshold] = useState("")
  const [filteredPollutants, setFilteredPollutants] = useState<Pollutant[]>([])

  // Fetch zones on mount
  useEffect(() => {
    fetchZones()
    fetchServiceHealth()
  }, [])

  const fetchZones = async () => {
    try {
      const res = await fetch("/api/aqi/zones")
      const data = await res.json()
      setZones(data.zones || [])
      if (data.zones?.length > 0) {
        setSelectedZone(data.zones[0])
      }
    } catch (error) {
      console.error("Error fetching zones:", error)
    }
  }

  const fetchServiceHealth = async () => {
    try {
      const res = await fetch("/api/aqi/health")
      const data = await res.json()
      setServiceHealth(data)
    } catch (error) {
      console.error("Error fetching service health:", error)
    }
  }

  const fetchAqi = async (zone: string) => {
    if (!zone) return
    try {
      const res = await fetch(`/api/aqi/${zone}`)
      const data = await res.json()
      setAqiData(data)
    } catch (error) {
      console.error("Error fetching AQI:", error)
    }
  }

  const fetchPollutants = async (zone: string) => {
    if (!zone) return
    try {
      const res = await fetch(`/api/aqi/pollutants/${zone}`)
      const data = await res.json()
      setPollutants(data.pollutants || [])
    } catch (error) {
      console.error("Error fetching pollutants:", error)
    }
  }

  const fetchHistory = async (zone: string) => {
    if (!zone) return
    try {
      const res = await fetch(`/api/aqi/history/${zone}`)
      const data = await res.json()
      setHistory(data.history || [])
    } catch (error) {
      console.error("Error fetching history:", error)
    }
  }

  const compareZones = async () => {
    if (!zoneA || !zoneB) return
    try {
      const res = await fetch(`/api/aqi/compare/${zoneA}/${zoneB}`)
      const data = await res.json()
      setComparison(data)
    } catch (error) {
      console.error("Error comparing zones:", error)
    }
  }

  const filterPollutants = async () => {
    if (!selectedZone || !threshold) return
    try {
      const res = await fetch(`/api/aqi/filter/${selectedZone}?threshold=${threshold}`)
      const data = await res.json()
      setFilteredPollutants(data.pollutants || [])
    } catch (error) {
      console.error("Error filtering pollutants:", error)
    }
  }

  const getAqiColor = (aqi: number) => {
    if (aqi <= 50) return "text-green-600"
    if (aqi <= 100) return "text-yellow-600"
    if (aqi <= 150) return "text-orange-600"
    return "text-red-600"
  }

  const getAqiBgColor = (aqi: number) => {
    if (aqi <= 50) return "bg-green-100 border-green-300"
    if (aqi <= 100) return "bg-yellow-100 border-yellow-300"
    if (aqi <= 150) return "bg-orange-100 border-orange-300"
    return "bg-red-100 border-red-300"
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground">Qualité de l'Air</h2>
          <p className="text-muted-foreground mt-1">Surveillance en temps réel de la qualité de l'air</p>
        </div>
        {serviceHealth && (
          <div className="flex items-center gap-2">
            {serviceHealth.status === "ok" ? (
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            <span className="text-sm text-muted-foreground">{serviceHealth.message}</span>
          </div>
        )}
      </div>

      {/* Zone Selection & AQI Display */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Wind className="h-5 w-5 text-primary" />
          <h3 className="text-xl font-semibold">Indice de Qualité de l'Air (AQI)</h3>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="zone-select">Sélectionner une zone</Label>
            <select
              id="zone-select"
              value={selectedZone}
              onChange={(e) => {
                setSelectedZone(e.target.value)
                fetchAqi(e.target.value)
                fetchPollutants(e.target.value)
                fetchHistory(e.target.value)
              }}
              className="w-full mt-1 px-3 py-2 border border-input rounded-md bg-background"
            >
              <option value="">-- Choisir une zone --</option>
              {zones.map((zone) => (
                <option key={zone} value={zone}>
                  {zone}
                </option>
              ))}
            </select>
          </div>

          {aqiData && (
            <div className={`p-6 rounded-lg border-2 ${getAqiBgColor(aqiData.aqi)}`}>
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-2">{aqiData.zone}</p>
                <p className={`text-6xl font-bold ${getAqiColor(aqiData.aqi)}`}>{aqiData.aqi}</p>
                <p className="text-lg font-medium mt-2">{aqiData.category}</p>
                <p className="text-xs text-muted-foreground mt-1">{new Date(aqiData.timestamp).toLocaleString()}</p>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Pollutants */}
      {pollutants.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="h-5 w-5 text-primary" />
            <h3 className="text-xl font-semibold">Polluants</h3>
          </div>

          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {pollutants.map((pollutant, idx) => (
              <div key={idx} className="p-4 border border-border rounded-lg">
                <p className="font-medium">{pollutant.name}</p>
                <p className="text-2xl font-bold text-primary mt-1">
                  {pollutant.value} <span className="text-sm text-muted-foreground">{pollutant.unit}</span>
                </p>
                <p className="text-sm text-muted-foreground mt-1">{pollutant.status}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Filter Pollutants */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-5 w-5 text-primary" />
          <h3 className="text-xl font-semibold">Filtrer les Polluants</h3>
        </div>

        <div className="flex gap-3">
          <div className="flex-1">
            <Label htmlFor="threshold">Seuil minimum</Label>
            <Input
              id="threshold"
              type="number"
              placeholder="Ex: 50"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
            />
          </div>
          <Button onClick={filterPollutants} className="mt-auto">
            Filtrer
          </Button>
        </div>

        {filteredPollutants.length > 0 && (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 mt-4">
            {filteredPollutants.map((pollutant, idx) => (
              <div key={idx} className="p-4 border border-border rounded-lg bg-accent/50">
                <p className="font-medium">{pollutant.name}</p>
                <p className="text-2xl font-bold text-primary mt-1">
                  {pollutant.value} <span className="text-sm text-muted-foreground">{pollutant.unit}</span>
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Comparison */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-5 w-5 text-primary" />
          <h3 className="text-xl font-semibold">Comparer deux zones</h3>
        </div>

        <div className="grid md:grid-cols-3 gap-3">
          <div>
            <Label htmlFor="zone-a">Zone A</Label>
            <select
              id="zone-a"
              value={zoneA}
              onChange={(e) => setZoneA(e.target.value)}
              className="w-full mt-1 px-3 py-2 border border-input rounded-md bg-background"
            >
              <option value="">-- Choisir --</option>
              {zones.map((zone) => (
                <option key={zone} value={zone}>
                  {zone}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label htmlFor="zone-b">Zone B</Label>
            <select
              id="zone-b"
              value={zoneB}
              onChange={(e) => setZoneB(e.target.value)}
              className="w-full mt-1 px-3 py-2 border border-input rounded-md bg-background"
            >
              <option value="">-- Choisir --</option>
              {zones.map((zone) => (
                <option key={zone} value={zone}>
                  {zone}
                </option>
              ))}
            </select>
          </div>

          <Button onClick={compareZones} className="mt-auto">
            Comparer
          </Button>
        </div>

        {comparison && (
          <div className="mt-4 p-4 border border-border rounded-lg bg-accent/50">
            <div className="grid md:grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-sm text-muted-foreground">{comparison.zoneA}</p>
                <p className={`text-3xl font-bold ${getAqiColor(comparison.aqiA)}`}>{comparison.aqiA}</p>
              </div>
              <div className="flex items-center justify-center">
                <div>
                  <p className="text-sm text-muted-foreground">Différence</p>
                  <p className="text-2xl font-bold text-primary">{Math.abs(comparison.difference)}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{comparison.zoneB}</p>
                <p className={`text-3xl font-bold ${getAqiColor(comparison.aqiB)}`}>{comparison.aqiB}</p>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* History */}
      {history.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Historique des mesures</h3>

          <div className="space-y-2">
            {history.map((point, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border border-border rounded-lg">
                <span className="text-sm text-muted-foreground">{new Date(point.timestamp).toLocaleString()}</span>
                <span className={`text-lg font-semibold ${getAqiColor(point.aqi)}`}>AQI: {point.aqi}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
