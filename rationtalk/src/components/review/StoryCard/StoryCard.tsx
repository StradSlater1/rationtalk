// src/components/review/StoryCard.tsx
import React from "react";
import "./StoryCard.css";

interface StoryCardProps {
  title: string;
  imageUrl: string;
  summary: string;
}

export default function StoryCard({
  title,
  imageUrl,
  summary,
}: StoryCardProps) {
  return (
    <div className="story-card">
      <br></br>
      <div className="story-header">
        <img
          src={`http://localhost:4000/api/proxy-image?url=${encodeURIComponent(
            imageUrl
          )}`}
          alt={title}
          className="story-image"
        />
        <h2 className="story-title">{title}</h2>
      </div>
      <p className="story-summary">{summary}</p>
    </div>
  );
}
