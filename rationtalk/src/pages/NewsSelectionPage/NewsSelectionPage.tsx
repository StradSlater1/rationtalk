// src/pages/NewSelectionPage.tsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // ← import useNavigate
import Header from "../../components/news_selection/Header/Header";
import NewsForm from "../../components/news_selection/NewsForm/NewsForm";
import "./NewsSelectionPage.css"; // optional, if you have page‐specific styles

export default function NewSelectionPage(): React.JSX.Element {
  const [selectedSections, setSelectedSections] = useState<string[]>([]);
  const [articleCount, setArticleCount] = useState<number>(1);

  const navigate = useNavigate();

  const handleToggleSection = (section: string) => {
    setSelectedSections((prev) =>
      prev.includes(section)
        ? prev.filter((s) => s !== section)
        : [...prev, section]
    );
  };

  const handleIncrement = () => setArticleCount((c) => c + 1);
  const handleDecrement = () => setArticleCount((c) => Math.max(1, c - 1));

  const handleSubmit = () => {
    console.log("Submitting to /review with:", {
      selectedSections,
      articleCount,
    });

    navigate("/review", {
      state: {
        selectedSections,
        articleCount,
      },
    });
  };

  return (
    <div className="new-selection-page">
      <Header />

      <NewsForm
        selectedSections={selectedSections}
        onToggleSection={handleToggleSection}
        articleCount={articleCount}
        onIncrement={handleIncrement}
        onDecrement={handleDecrement}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
