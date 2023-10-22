import React from "react";
import NavBar from "./components/navigation/NavBar";
import { Route, Routes } from "react-router-dom";

import CallbackPage from "./pages/CallbackPage";
import HomePage from "./pages/PublicPage";
import MyInfoPage from "./pages/MyInfoPage";

export default function App() {
  return (
    <div className="app">
      <NavBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/callback" element={<CallbackPage />} />
        <Route path="/me" element={<MyInfoPage />} />
      </Routes>
    </div>
  );
}
