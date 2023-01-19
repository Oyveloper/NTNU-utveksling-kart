import "./App.css";
import Map from "./Map";
import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import ClipLoader from "react-spinners/ClipLoader";

const BASE_URL = "https://ntnu-utveksling-function-xopihvxzkq-ew.a.run.app/";
/* const BASE_URL = "http://localhost:8080/"; */

function App() {
  const location = useLocation();
  const [data, setData] = useState();
  const search = location.search.split("=")[1];

  const [inputValue, setInputValue] = useState(search);

  useEffect(() => {
    fetch(`${BASE_URL}/stats/?search=${search || ""}`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
      });
  }, [search]);

  return (
    <div className="App">
      <h1>Sjekk hvor mange som har vært på utveksling i hvert land!</h1>

      <p>
        Dataen er basert på rapporter i{" "}
        <a href="https://www.ntnu.no/studier/studier_i_utlandet/rapport/table.php">
          NTNU sin database
        </a>{" "}
        over utvekslingsrapporter, og kan inneholde noen feil da ikke alle har
        skrevet rapport, og rapportene kun går tilbake til 2015. Du kan søke
        etter ditt studieprogram under, eller la feltet stå blankt for å se
        alle.
      </p>

      <form>
        <input
          type="text"
          name="search"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button type="submit" method="/">
          Søk
        </button>
      </form>

      {data ? (
        <Map countries={data} />
      ) : (
        <div
          style={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <ClipLoader />
        </div>
      )}
      <p>Øyvind Monsen, 2023</p>
    </div>
  );
}

export default App;
