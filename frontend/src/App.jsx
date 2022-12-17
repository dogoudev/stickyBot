import React, { useState } from "react";
import logo from "./logo.svg";
import "./App.css";
import Album from "./Album.jsx";

function App() {
  let el = document.createElement("a");
  el.href = window.location.href;
  const albumId = el.pathname.split("/")[2] || "";

  const [albumName, setAlbumName] = useState("");

  return (
    <div className="App">
      <header className="App-header">
        <p>{albumName}</p>
      </header>

      <div>
        <Album albumId={albumId} setAlbumName={setAlbumName} />
      </div>
    </div>
  );
}

export default App;
