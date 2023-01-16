import "./App.css";
import Map from "./Map";
import { useState, useEffect } from "react";

function App() {
  const [data, setData] = useState({});

  useEffect(() => {
    // fetch("http://localhost:8080/")
    fetch(
      "https://utveksling-stats-bucket.storage.googleapis.com/country_counts.json"
    )
      .then((res) => res.json())
      .then((data) => {
        setData(data);
      });
  }, []);

  return (
    <div className='App'>
      <h1>Sjekk hvor mange som har vært på utveksling i hvert land!</h1>
      <Map countries={data} />
      <p>Øyvind Monsen, 2023</p>
    </div>
  );
}

export default App;
