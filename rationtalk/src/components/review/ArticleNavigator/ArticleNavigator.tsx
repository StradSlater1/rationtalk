// src/components/review/ArticleNavigator.tsx
import React from "react";
import "./ArticleNavigator.css";

interface ArticleNavigatorProps {
  currentIndex: number; // zero‐based
  totalStories: number; // e.g. 5
  onPrevious: () => void;
  onNext: () => void;
}

export default function ArticleNavigator({
  currentIndex,
  totalStories,
  onPrevious,
  onNext,
}: ArticleNavigatorProps) {
  return (
    <div className="article-navigator">
      <button
        className="nav-button"
        onClick={onPrevious}
        disabled={currentIndex === 0}
      >
        ← Previous article
      </button>

      <span className="nav-status">
        {currentIndex + 1} of {totalStories}
      </span>

      <button
        className="nav-button"
        onClick={onNext}
        disabled={currentIndex + 1 >= totalStories}
      >
        Next article →
      </button>
    </div>
  );
}
