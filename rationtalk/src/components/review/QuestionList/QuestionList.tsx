// src/components/review/QuestionList.tsx
import React from "react";
import QuestionItem from "../QuestionItem/QuestionItem.tsx";
import "./QuestionList.css";

interface QuestionListProps {
  questions: string[];
  responses: string[];
  onResponseChange: (index: number, newValue: string) => void;
}

export default function QuestionList({
  questions,
  responses,
  onResponseChange,
}: QuestionListProps) {
  return (
    <div className="question-list">
      <br></br>
      <h1 className="question-list-header">Questions</h1>
      {questions.map((q, idx) => (
        <QuestionItem
          key={idx}
          questionText={`${q}`}
          responseValue={responses[idx] || ""}
          onResponseChange={(newVal) => onResponseChange(idx, newVal)}
        />
      ))}
    </div>
  );
}
