import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";
import { memo, useState } from "react";
import { Tooltip } from "react-tooltip";
import { scalePow } from "d3-scale";
const geoUrl =
  "https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries.json";
function Map(props) {
  const { countries } = props;
  const [hoverName, setHoverName] = useState("");
  const max = countries ? Math.max(...Object.values(countries)) : 0;
  const colorScale = scalePow()
    .exponent(0.4)
    .domain([0, max])
    .range(["#cfebf4", "#20a2d5"]);
  return (
    <div id="map-container">
      <Tooltip
        anchorId="map"
        content={hoverName}
        float={true}
        variant="info"
        place="right"
        noArrow
      />

      <div id="map">
        <ComposableMap>
          <ZoomableGroup center={[0, 0]} zoom={1}>
            <Geographies geography={geoUrl}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  let count = 0;
                  if (countries && countries[geo.properties.name]) {
                    count = countries[geo.properties.name];
                  }
                  let color = colorScale(count);
                  let darkercolor = colorScale(count + 50);

                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={color}
                      onMouseEnter={() => {
                        let stats = "0";
                        if (countries && countries[geo.properties.name]) {
                          stats = countries[geo.properties.name];
                        }
                        setHoverName(`${geo.properties.name}: ${stats}`);
                      }}
                      onMouseLeave={() => {
                        setHoverName("");
                      }}
                      style={{
                        default: {
                          transition: "all 250ms",
                          stroke: "#fff",
                          //   "stroke-width": 0.5,
                        },
                        hover: {
                          stroke: "var(--rt-color-warning)",
                          zIndex: 2,
                          strokeWidth: 2,
                          fill: darkercolor,
                        },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>
      </div>
    </div>
  );
}
export default memo(Map);
