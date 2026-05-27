"use client";

import { useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from "react-simple-maps";

import { lookupCity } from "@/lib/cities";
import type { CityHeat } from "@/lib/api";

/**
 * Path served from /public. See public/maps/README.md for how to obtain
 * the india-states topojson. We fail gracefully if the file is missing.
 */
const GEO_URL = "/maps/india-states.json";

type Props = {
  cities: CityHeat[];
};

type HoverState = {
  city: CityHeat;
  x: number;
  y: number;
} | null;

export default function IndiaHeatmap({ cities }: Props) {
  const [hover, setHover] = useState<HoverState>(null);

  const max = Math.max(1, ...cities.map((c) => c.job_count));
  const placed = cities
    .map((c) => ({ data: c, coords: lookupCity(c.city) }))
    .filter((x): x is { data: CityHeat; coords: [number, number] } => x.coords !== null);
  const unplaced = cities.length - placed.length;

  return (
    <div className="relative">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{ center: [82, 22], scale: 1000 }}
        width={800}
        height={700}
        style={{ width: "100%", height: "auto" }}
      >
        <Geographies geography={GEO_URL}>
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill="#f4f4f5"
                stroke="#d4d4d8"
                strokeWidth={0.5}
                style={{
                  default: { outline: "none" },
                  hover: { fill: "#e4e4e7", outline: "none" },
                  pressed: { outline: "none" },
                }}
              />
            ))
          }
        </Geographies>

        {placed.map(({ data, coords }) => {
          const radius = 4 + Math.sqrt(data.job_count / max) * 22;
          return (
            <Marker
              key={data.city}
              coordinates={coords}
              onMouseEnter={(e) =>
                setHover({ city: data, x: e.clientX, y: e.clientY })
              }
              onMouseMove={(e) =>
                setHover({ city: data, x: e.clientX, y: e.clientY })
              }
              onMouseLeave={() => setHover(null)}
            >
              <circle
                r={radius}
                fill="rgba(16, 185, 129, 0.55)"
                stroke="#047857"
                strokeWidth={1.5}
                className="cursor-pointer transition-all hover:fill-emerald-500"
              />
              <text
                textAnchor="middle"
                y={-radius - 4}
                className="pointer-events-none fill-zinc-700 text-[10px] font-medium dark:fill-zinc-200"
              >
                {data.city}
              </text>
            </Marker>
          );
        })}
      </ComposableMap>

      {hover && (
        <div
          className="pointer-events-none fixed z-50 rounded-md border border-zinc-200 bg-white px-3 py-2 text-xs shadow-lg dark:border-zinc-700 dark:bg-zinc-900"
          style={{ left: hover.x + 12, top: hover.y + 12 }}
        >
          <div className="font-semibold">{hover.city.city}</div>
          <div className="tabular-nums text-zinc-600 dark:text-zinc-400">
            {hover.city.job_count} active jobs
          </div>
          {hover.city.top_skills.length > 0 && (
            <div className="mt-1 max-w-[220px] text-zinc-500">
              {hover.city.top_skills.slice(0, 5).join(" · ")}
            </div>
          )}
        </div>
      )}

      {unplaced > 0 && (
        <p className="mt-2 text-xs text-zinc-500">
          {unplaced} cities not plotted (missing coordinates in
          <code className="mx-1 rounded bg-zinc-100 px-1 py-0.5 dark:bg-zinc-800">
            lib/cities.ts
          </code>
          ).
        </p>
      )}
    </div>
  );
}
