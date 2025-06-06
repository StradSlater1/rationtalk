// src/App.tsx
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NewSelectionPage from "./pages/NewsSelectionPage/NewsSelectionPage.tsx";
import ReviewPage from "./pages/ReviewPage/ReviewPage.tsx"; // assume you’ll create this
import { storiestouse } from "./assets/data/stories"; // import your stories

export default function App(): React.JSX.Element {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NewSelectionPage />} />
        <Route path="/review" element={<ReviewPage stories={storiestouse} />} />
      </Routes>
    </BrowserRouter>
  );
}
