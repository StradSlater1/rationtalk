import "./EmailModal.css";

import React, { useState } from "react";
import "./EmailModal.css";

interface EmailModalProps {
  onClose: () => void;
  onSend: (email: string) => void;
}

export default function EmailModal({ onClose, onSend }: EmailModalProps) {
  const [email, setEmail] = useState("");

  const handleSendClick = () => {
    // You can add simple validation here if you want:
    if (!email || !email.includes("@")) {
      alert("Please enter a valid email address.");
      return;
    }
    onSend(email);
  };

  return (
    <div className="email-modal-backdrop">
      <div className="email-modal">
        <button className="email-modal-close" onClick={onClose}>
          &times;
        </button>
        <h2>Send Responses to Email</h2>
        <p>Enter your email address below:</p>
        <input
          type="email"
          className="email-modal-input"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button className="email-modal-send" onClick={handleSendClick}>
          Send
        </button>
      </div>
    </div>
  );
}
