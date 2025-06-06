// src/components/review/ReviewHeader.tsx
import React from "react";
import "./ReviewHeader.css";

interface ReviewHeaderProps {
  onBack: () => void;
  onSendEmail: () => void;
}

export default function ReviewHeader({
  onBack,
  onSendEmail,
}: ReviewHeaderProps) {
  return (
    <header className="review-header">
      <button className="back-button" onClick={onBack}>
        ← Back to article selection
      </button>
      <div className="logo-title">
        {/* You can reuse your RationTalk <Header> or just render the logo+text here */}
        <h1 className="logo">
          <i className="fa-solid fa-comment"></i>
          RationTalk
        </h1>
      </div>
      <button className="send-email" onClick={onSendEmail}>
        Send responses to email ✈
      </button>
    </header>
  );
}
