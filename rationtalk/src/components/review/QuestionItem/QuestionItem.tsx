// src/components/review/QuestionItem.tsx
import React from "react";
import "./QuestionItem.css";
import { useRef, useEffect } from "react";

interface QuestionItemProps {
  questionText: string;
  responseValue: string;
  onResponseChange: (newValue: string) => void;
}

export default function QuestionItem({
  questionText,
  responseValue,
  onResponseChange,
}: QuestionItemProps) {
  // We'll keep a ref to the textarea so we can resize it on mount and on each input
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Function to auto-resize the textarea
  const autoResize = () => {
    if (!textareaRef.current) return;
    const ta = textareaRef.current;

    ta.style.height = "auto"; // reset to auto to shrink if content was removed
    ta.style.height = ta.scrollHeight + "px"; // set height to match content
  };

  // When the component first mounts, auto‐expand if there's any initial text
  useEffect(() => {
    autoResize();
  }, []);
  return (
    <div className="question-item">
      <div className="question-text">{questionText}</div>
      <textarea
        ref={textareaRef}
        className="response-input"
        value={responseValue}
        onChange={(e) => onResponseChange(e.target.value)}
        rows={3}
        placeholder=""
        onInput={autoResize}
      />
    </div>
  );
}
