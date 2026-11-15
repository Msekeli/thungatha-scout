import React from "react";
import ReactDOM from "react-dom/client";
import { ScoutAuthGate } from "./app-authentication/ScoutAuthGate";
import "./styles.css";
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ScoutAuthGate />
  </React.StrictMode>,
);
