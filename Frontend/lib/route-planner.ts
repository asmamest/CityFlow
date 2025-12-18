/**
 * Fonction de planification d'itinéraires pour une application de mobilité urbaine
 * Utilise les endpoints backend existants pour calculer des itinéraires directs et avec correspondances
 */

// Types TypeScript
interface Ligne {
  numero: string;
  nom: string;
  type_transport: string;
  terminus_debut: string;
  terminus_fin: string;
  actif: boolean;
  id: string;
}

interface Horaire {
  id: string;
  ligne_id: string;
  destination: string;
  heure_depart: string;
  heure_arrivee: string;
  station: string;
  quai: string;
}

interface ItineraireSegment {
  ligne: string;
  depart: string;
  arrivee: string;
  duree_minutes: number;
  type: string;
}

interface Itineraire {
  itineraire_id: number;
  depart: string;
  arrivee: string;
  duree_totale_minutes: number;
  nombre_correspondances: number;
  heure_depart: string;
  heure_arrivee: string;
  segments: ItineraireSegment[];
}

interface PlanificationResult {
  timestamp: string;
  nombre_itineraires: number;
  itineraires: Itineraire[];
}

/**
 * Fonction principale de planification d'itinéraires
 * @param depart - Station de départ
 * @param arrivee - Station d'arrivée
 * @param heureDepart - Heure de départ souhaitée (format HH:MM, optionnel)
 * @param backendUrl - URL du backend (par défaut http://localhost:8000)
 * @returns Promesse contenant les itinéraires trouvés
 */
export async function planifierItineraire(
  depart: string,
  arrivee: string,
  heureDepart?: string,
  backendUrl: string = "http://localhost:8000"
): Promise<PlanificationResult> {
  try {
    // 1. Récupérer toutes les lignes disponibles
    const lignes = await fetchLignes(backendUrl);
    
    // 2. Récupérer les horaires de toutes les lignes
    const horairesByLigne = await fetchAllHoraires(lignes, backendUrl);
    
    // 3. Trouver les itinéraires directs
    const itinerairesDirects = findDirectRoutes(
      depart,
      arrivee,
      lignes,
      horairesByLigne,
      heureDepart
    );
    
    // 4. Trouver les itinéraires avec 1 correspondance
    const itinerairesAvecCorrespondance = findRoutesWithTransfer(
      depart,
      arrivee,
      lignes,
      horairesByLigne,
      heureDepart
    );
    
    // 5. Combiner et trier les itinéraires par durée
    const tousLesItineraires = [...itinerairesDirects, ...itinerairesAvecCorrespondance]
      .sort((a, b) => a.duree_totale_minutes - b.duree_totale_minutes)
      .slice(0, 5); // Limiter à 5 meilleurs itinéraires
    
    return {
      timestamp: new Date().toISOString(),
      nombre_itineraires: tousLesItineraires.length,
      itineraires: tousLesItineraires,
    };
  } catch (error) {
    console.error("Erreur lors de la planification:", error);
    throw error;
  }
}

/**
 * Récupère toutes les lignes depuis le backend
 */
async function fetchLignes(backendUrl: string): Promise<Ligne[]> {
  const response = await fetch(`${backendUrl}/lignes`);
  if (!response.ok) throw new Error("Erreur lors de la récupération des lignes");
  return response.json();
}

/**
 * Récupère les horaires de toutes les lignes
 */
async function fetchAllHoraires(
  lignes: Ligne[],
  backendUrl: string
): Promise<Map<string, Horaire[]>> {
  const horairesByLigne = new Map<string, Horaire[]>();
  
  // Récupérer les horaires pour chaque ligne en parallèle
  const promises = lignes.map(async (ligne) => {
    try {
      const response = await fetch(`${backendUrl}/horaires/${ligne.numero}`);
      if (response.ok) {
        const data = await response.json();
        horairesByLigne.set(ligne.id, data.horaires || []);
      }
    } catch (error) {
      console.warn(`Erreur pour la ligne ${ligne.numero}:`, error);
    }
  });
  
  await Promise.all(promises);
  return horairesByLigne;
}

/**
 * Trouve tous les itinéraires directs (sans correspondance)
 */
function findDirectRoutes(
  depart: string,
  arrivee: string,
  lignes: Ligne[],
  horairesByLigne: Map<string, Horaire[]>,
  heureDepart?: string
): Itineraire[] {
  const itineraires: Itineraire[] = [];
  let itineraireId = 1;
  
  // Pour chaque ligne, vérifier si elle dessert les deux stations
  for (const ligne of lignes) {
    const horaires = horairesByLigne.get(ligne.id) || [];
    
    // Trouver les horaires qui partent de la station de départ
    const horairesDep = horaires.filter((h) =>
      normalizeStation(h.station) === normalizeStation(depart)
    );
    
    // Trouver les horaires qui arrivent à la station d'arrivée
    const horairesArr = horaires.filter((h) =>
      normalizeStation(h.destination) === normalizeStation(arrivee)
    );
    
    // Si la ligne dessert les deux stations
    if (horairesDep.length > 0 && horairesArr.length > 0) {
      // Créer un itinéraire pour chaque horaire de départ valide
      for (const horaireDep of horairesDep) {
        // Filtrer par heure de départ si spécifiée
        if (heureDepart && horaireDep.heure_depart < heureDepart) {
          continue;
        }
        
        // Trouver un horaire d'arrivée correspondant
        const horaireArr = horairesArr.find(
          (h) => h.heure_depart >= horaireDep.heure_depart
        );
        
        if (horaireArr) {
          const duree = calculateDuration(
            horaireDep.heure_depart,
            horaireArr.heure_arrivee
          );
          
          itineraires.push({
            itineraire_id: itineraireId++,
            depart: depart,
            arrivee: arrivee,
            duree_totale_minutes: duree,
            nombre_correspondances: 0,
            heure_depart: horaireDep.heure_depart,
            heure_arrivee: horaireArr.heure_arrivee,
            segments: [
              {
                ligne: ligne.numero,
                depart: depart,
                arrivee: arrivee,
                duree_minutes: duree,
                type: capitalizeFirst(ligne.type_transport),
              },
            ],
          });
        }
      }
    }
  }
  
  return itineraires;
}

/**
 * Trouve les itinéraires avec 1 correspondance
 */
function findRoutesWithTransfer(
  depart: string,
  arrivee: string,
  lignes: Ligne[],
  horairesByLigne: Map<string, Horaire[]>,
  heureDepart?: string
): Itineraire[] {
  const itineraires: Itineraire[] = [];
  let itineraireId = 1000; // ID différent pour les itinéraires avec correspondance
  
  // Trouver toutes les stations intermédiaires possibles
  const stationsIntermediaires = findIntermediateStations(
    depart,
    arrivee,
    lignes,
    horairesByLigne
  );
  
  // Pour chaque station intermédiaire
  for (const stationInter of stationsIntermediaires) {
    // Trouver les lignes qui vont de départ à stationInter
    for (const ligne1 of lignes) {
      const horaires1 = horairesByLigne.get(ligne1.id) || [];
      const segment1Options = findSegmentOptions(
        depart,
        stationInter,
        horaires1,
        heureDepart
      );
      
      if (segment1Options.length === 0) continue;
      
      // Pour chaque option du premier segment
      for (const seg1 of segment1Options) {
        // Trouver les lignes qui vont de stationInter à arrivee
        for (const ligne2 of lignes) {
          // Éviter de prendre la même ligne deux fois (sauf si vraiment nécessaire)
          if (ligne1.id === ligne2.id) continue;
          
          const horaires2 = horairesByLigne.get(ligne2.id) || [];
          // Le deuxième segment doit partir après l'arrivée du premier (+ temps de correspondance)
          const heureMinCorrespondance = addMinutes(seg1.heure_arrivee, 5);
          
          const segment2Options = findSegmentOptions(
            stationInter,
            arrivee,
            horaires2,
            heureMinCorrespondance
          );
          
          if (segment2Options.length === 0) continue;
          
          // Prendre la première option du deuxième segment
          const seg2 = segment2Options[0];
          
          const dureeSegment1 = calculateDuration(
            seg1.heure_depart,
            seg1.heure_arrivee
          );
          const dureeSegment2 = calculateDuration(
            seg2.heure_depart,
            seg2.heure_arrivee
          );
          const dureeAttente = calculateDuration(
            seg1.heure_arrivee,
            seg2.heure_depart
          );
          const dureeTotale = dureeSegment1 + dureeSegment2 + dureeAttente;
          
          itineraires.push({
            itineraire_id: itineraireId++,
            depart: depart,
            arrivee: arrivee,
            duree_totale_minutes: dureeTotale,
            nombre_correspondances: 1,
            heure_depart: seg1.heure_depart,
            heure_arrivee: seg2.heure_arrivee,
            segments: [
              {
                ligne: ligne1.numero,
                depart: depart,
                arrivee: stationInter,
                duree_minutes: dureeSegment1,
                type: capitalizeFirst(ligne1.type_transport),
              },
              {
                ligne: ligne2.numero,
                depart: stationInter,
                arrivee: arrivee,
                duree_minutes: dureeSegment2,
                type: capitalizeFirst(ligne2.type_transport),
              },
            ],
          });
        }
      }
    }
  }
  
  return itineraires;
}

/**
 * Trouve toutes les stations intermédiaires possibles pour une correspondance
 */
function findIntermediateStations(
  depart: string,
  arrivee: string,
  lignes: Ligne[],
  horairesByLigne: Map<string, Horaire[]>
): string[] {
  const stations = new Set<string>();
  
  // Collecter toutes les stations desservies
  for (const ligne of lignes) {
    const horaires = horairesByLigne.get(ligne.id) || [];
    for (const horaire of horaires) {
      stations.add(horaire.station);
      stations.add(horaire.destination);
    }
  }
  
  // Retirer le départ et l'arrivée
  stations.delete(normalizeStation(depart));
  stations.delete(normalizeStation(arrivee));
  
  return Array.from(stations);
}

/**
 * Trouve les options de segment entre deux stations sur une ligne donnée
 */
function findSegmentOptions(
  depart: string,
  arrivee: string,
  horaires: Horaire[],
  heureMin?: string
): Array<{ heure_depart: string; heure_arrivee: string }> {
  const options: Array<{ heure_depart: string; heure_arrivee: string }> = [];
  
  const horairesDep = horaires.filter(
    (h) => normalizeStation(h.station) === normalizeStation(depart)
  );
  const horairesArr = horaires.filter(
    (h) => normalizeStation(h.destination) === normalizeStation(arrivee)
  );
  
  for (const hDep of horairesDep) {
    if (heureMin && hDep.heure_depart < heureMin) continue;
    
    const hArr = horairesArr.find((h) => h.heure_depart >= hDep.heure_depart);
    if (hArr) {
      options.push({
        heure_depart: hDep.heure_depart,
        heure_arrivee: hArr.heure_arrivee,
      });
    }
  }
  
  return options;
}

/**
 * Calcule la durée en minutes entre deux heures (format HH:MM)
 */
function calculateDuration(heureDebut: string, heureFin: string): number {
  const [h1, m1] = heureDebut.split(":").map(Number);
  const [h2, m2] = heureFin.split(":").map(Number);
  
  const minutes1 = h1 * 60 + m1;
  const minutes2 = h2 * 60 + m2;
  
  let duree = minutes2 - minutes1;
  
  // Gérer le passage à minuit
  if (duree < 0) {
    duree += 24 * 60;
  }
  
  return duree;
}

/**
 * Ajoute des minutes à une heure (format HH:MM)
 */
function addMinutes(heure: string, minutes: number): string {
  const [h, m] = heure.split(":").map(Number);
  const totalMinutes = h * 60 + m + minutes;
  const newH = Math.floor(totalMinutes / 60) % 24;
  const newM = totalMinutes % 60;
  
  return `${String(newH).padStart(2, "0")}:${String(newM).padStart(2, "0")}`;
}

/**
 * Normalise le nom d'une station pour la comparaison
 */
function normalizeStation(station: string): string {
  return station.toLowerCase().trim();
}

/**
 * Met en majuscule la première lettre
 */
function capitalizeFirst(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/**
 * Exemple d'utilisation dans votre composant React
 */
export async function handlePlanification(
  depart: string,
  arrivee: string,
  heureDepart?: string
): Promise<PlanificationResult> {
  try {
    const result = await planifierItineraire(depart, arrivee, heureDepart);
    return result;
  } catch (error) {
    console.error("Erreur de planification:", error);
    // Retourner un résultat vide en cas d'erreur
    return {
      timestamp: new Date().toISOString(),
      nombre_itineraires: 0,
      itineraires: [],
    };
  }
}