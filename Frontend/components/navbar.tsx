"use client"

import { Train } from "lucide-react"

interface NavbarProps {
  activeSection: "lignes" | "trafic" | "horaires" | "disponibilite" | "planification" | "aqi"
  setActiveSection: (section: "lignes" | "trafic" | "horaires" | "disponibilite" | "planification" | "aqi") => void
}

export function Navbar({ activeSection, setActiveSection }: NavbarProps) {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
              <Train className="h-6 w-6 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-semibold text-foreground">Service de Mobilité </h1>
          </div>

          <nav className="flex gap-1">
            <button
              onClick={() => setActiveSection("lignes")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === "lignes"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              Lignes
            </button>
            <button
              onClick={() => setActiveSection("trafic")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === "trafic"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              Trafic
            </button>
            <button
              onClick={() => setActiveSection("horaires")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === "horaires"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              Horaires
            </button>
            <button
              onClick={() => setActiveSection("disponibilite")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === "disponibilite"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              Disponibilité
            </button>
            <button
              onClick={() => setActiveSection("planification")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === "planification"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              Planification
            </button>
            <button
              onClick={() => setActiveSection("aqi")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeSection === "aqi"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent"
              }`}
            >
              Qualité Air
            </button>
          </nav>
        </div>
      </div>
    </header>
  )
}
