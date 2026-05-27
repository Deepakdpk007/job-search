# Map data

The India heatmap (`/heatmap`) loads `india-states.json` from this directory
at runtime. The file is **not committed** because it's third-party map data.

## How to obtain it

Download a state-level India TopoJSON. A widely-used, MIT-licensed source is:

```bash
curl -L https://raw.githubusercontent.com/deldersveld/topojson/master/countries/india/india-states.json \
  -o web/public/maps/india-states.json
```

That's ~120 KB. Verify it's valid JSON:

```bash
python -c "import json; json.load(open('web/public/maps/india-states.json'))"
```

After this, restart `npm run dev` and the map will render.

## If you don't add the file

The page still works — the `<Geographies>` component fails silently and you'll
see the city bubbles on a blank background. Markers and tooltips are unaffected.

## Alternative sources

- [datameet/maps](https://github.com/datameet/maps) — official Indian district
  and state maps, but you'll need to convert the shapefiles to TopoJSON.
- [DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector)
  — covers many countries; pick India.

If you swap in a different file, update `GEO_URL` in
`components/india-heatmap.tsx`.
