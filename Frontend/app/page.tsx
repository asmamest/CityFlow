"use client"

import { useState } from "react"
import { Navbar } from "@/components/navbar"
import { LignesSection } from "@/components/lignes-section"
import { TraficSection } from "@/components/trafic-section"
import { HorairesSection } from "@/components/horaires-section"
import { DisponibiliteSection } from "@/components/disponibilite-section"
import { PlanificationSection } from "@/components/planification-section"
import { AqiSection } from "@/components/aqi-section"
import { Footer } from "@/components/footer"

export default function Home() {
  const [activeSection, setActiveSection] = useState<
    "lignes" | "trafic" | "horaires" | "disponibilite" | "planification" | "aqi"
  >("lignes")

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar activeSection={activeSection} setActiveSection={setActiveSection} />

      <main className="flex-1 container mx-auto px-4 py-8 md:py-12">
        {activeSection === "lignes" && <LignesSection />}
        {activeSection === "trafic" && <TraficSection />}
        {activeSection === "horaires" && <HorairesSection />}
        {activeSection === "disponibilite" && <DisponibiliteSection />}
        {activeSection === "planification" && <PlanificationSection />}
        {activeSection === "aqi" && <AqiSection />}
      </main>

      <Footer />
    </div>
  )
}
