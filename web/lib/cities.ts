/**
 * Coordinates for major Indian hiring hubs.
 * Order: [longitude, latitude] (GeoJSON / d3-geo convention).
 *
 * Keys must match the canonical city strings produced by the API's
 * normalizer (see api/app/ingestion/normalizer.py).
 */
export const CITY_COORDS: Record<string, [number, number]> = {
  Bengaluru: [77.5946, 12.9716],
  Hyderabad: [78.4867, 17.385],
  Chennai: [80.2707, 13.0827],
  Mumbai: [72.8777, 19.076],
  Pune: [73.8567, 18.5204],
  Gurgaon: [77.0266, 28.4595],
  Noida: [77.391, 28.5355],
  Delhi: [77.1025, 28.7041],
  "Delhi NCR": [77.1025, 28.7041],
  Kolkata: [88.3639, 22.5726],
  Ahmedabad: [72.5714, 23.0225],
  Kochi: [76.2673, 9.9312],
  Thiruvananthapuram: [76.9366, 8.5241],
  Jaipur: [75.7873, 26.9124],
  Indore: [75.8577, 22.7196],
  Coimbatore: [76.9558, 11.0168],
};

/** Returns [lng, lat] or null if the city is not in our mapping. */
export function lookupCity(city: string): [number, number] | null {
  return CITY_COORDS[city] ?? null;
}
