import React from "react";
import logo from "./logo.svg";
import "./App.css";
import Album from "./Album.jsx";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p>Album</p>
      </header>

      <div>
        <Album />
      </div>
    </div>
  );
}

export default App;
