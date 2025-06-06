// src/components/review/ReviewPage.tsx
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import ReviewHeader from "../../components/review/ReviewHeader/ReviewHeader.tsx";
import StoryCard from "../../components/review/StoryCard/StoryCard.tsx";
import QuestionList from "../../components/review/QuestionList/QuestionList.tsx";
import ArticleNavigator from "../../components/review/ArticleNavigator/ArticleNavigator.tsx";
import EmailModal from "../../components/review/EmailModal/EmailModal.tsx";
import "./ReviewPage.css";
import axios from "axios";

// 1) Import the master list of all stories and the interleaving helper:
import type { StoryData } from "../../assets/data/stories";
import { interleaveByTopic } from "../../utils/story_sorter.tsx";

const APPS_SCRIPT_URL = "/api/google-form";

interface ReviewPageProps {
  stories: StoryData[];
}

interface LocationState {
  selectedSections: string[];
  articleCount: number;
}

export default function ReviewPage({
  stories,
}: ReviewPageProps): React.JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | undefined;

  // If the user navigated here without state, send them back:
  useEffect(() => {
    if (!state) {
      navigate("/", { replace: true });
    }
  }, [navigate, state]);

  // Once we're past that check, we know state is defined:
  const selectedSections = state?.selectedSections || [];
  const articleCount = state?.articleCount || 0;

  // 2) Filter the master story list to only those whose topic is selected:
  const filteredStories: StoryData[] = stories.filter((story) =>
    selectedSections.includes(story.topic)
  );

  // 3) Interleave by the order in selectedSections:
  const interleavedStories: StoryData[] = interleaveByTopic(
    filteredStories,
    selectedSections
  );

  // 4) Take only the first `articleCount` stories from that interleaved array:
  const storiesToShow: StoryData[] = interleavedStories.slice(0, articleCount);

  const totalStories = storiesToShow.length;
  const [currentIndex, setCurrentIndex] = useState(0);

  // 5) Initialize a parallel responses array for exactly those chosen stories:
  const [responses, setResponses] = useState<string[][]>(() =>
    storiesToShow.map((story) => story.questions.map(() => ""))
  );

  // 6) Control Email modal visibility
  const [showEmailModal, setShowEmailModal] = useState(false);

  const handleResponseChange = (qIdx: number, newVal: string) => {
    setResponses((prev) => {
      const copy = prev.map((arr) => [...arr]);
      copy[currentIndex][qIdx] = newVal;
      return copy;
    });
  };

  const goPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((i) => i - 1);
    }
  };

  const goNext = () => {
    if (currentIndex + 1 < totalStories) {
      setCurrentIndex((i) => i + 1);
    }
  };

  const handleBackToSelection = () => {
    navigate("/");
  };

  const handleSendEmailClick = () => {
    setShowEmailModal(true);
  };

  // 7) When the user submits email, flatten only the stories we actually show:
  const handleSendEmail = async (email: string) => {
    const flatQuestions: string[] = [];
    const flatAnswers: string[] = [];

    storiesToShow.forEach((story, sIdx) => {
      const { title: sTitle, summary: sSummary, questions: sQuestions } = story;
      const thisStoryAnswers = responses[sIdx];

      // One “story header” entry (no answer expected)
      flatQuestions.push(`${sTitle}\n\n${sSummary}`);
      flatAnswers.push("");

      // Then each question and its answer:
      sQuestions.forEach((qText, qIdx) => {
        flatQuestions.push(qText);
        flatAnswers.push(thisStoryAnswers[qIdx] || "");
      });
    });

    const formBody = new URLSearchParams();
    formBody.append("email", email);
    formBody.append("formTitle", "RationTalk: Selected Stories & Responses");
    formBody.append("storyTitle", "Your Selected Stories");
    formBody.append(
      "storySummary",
      "Below are the stories (in interleaved order) and your answers."
    );
    formBody.append("questions", JSON.stringify(flatQuestions));
    formBody.append("answers", JSON.stringify(flatAnswers));

    try {
      const res = await axios.post(APPS_SCRIPT_URL, formBody.toString(), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      if (res.data && res.data.success) {
        alert("Responses emailed! Check your inbox.");
      } else {
        console.error("Apps Script error:", res.data.error);
        alert("Failed to send email: " + (res.data.error || "Unknown error"));
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("Error sending to email. Check console for details.");
    } finally {
      setShowEmailModal(false);
    }
  };

  const handleCloseModal = () => {
    setShowEmailModal(false);
  };

  // If there are no stories to show (e.g. articleCount was zero), we can render a fallback:
  if (storiesToShow.length === 0) {
    return (
      <div className="review-page-container">
        <ReviewHeader
          onBack={handleBackToSelection}
          onSendEmail={handleSendEmailClick}
        />
        <main className="review-main">
          <p style={{ padding: "2rem", textAlign: "center" }}>
            No stories to display. Please go back and select at least one
            section.
          </p>
        </main>
      </div>
    );
  }

  const story = storiesToShow[currentIndex];

  return (
    <div className="review-page-container">
      {/* 1) Top header with back‐link & send‐email button */}
      <ReviewHeader
        onBack={handleBackToSelection}
        onSendEmail={handleSendEmailClick}
      />

      {/* 2) Main scrollable area (two columns) */}
      <main className="review-main">
        <div className="columns-wrapper">
          {/* Left: story card */}
          <div className="story-column">
            <div className="story-scrollable">
              <StoryCard
                title={story.title}
                imageUrl={story.imageUrl}
                summary={story.summary}
              />
            </div>
          </div>

          {/* Right: questions for the current story */}
          <div className="questions-column">
            <div className="questions-scrollable">
              <QuestionList
                questions={story.questions}
                responses={responses[currentIndex]}
                onResponseChange={handleResponseChange}
              />
            </div>
          </div>
        </div>
      </main>

      {/* 3) Fixed footer navigator */}
      <ArticleNavigator
        currentIndex={currentIndex}
        totalStories={totalStories}
        onPrevious={goPrevious}
        onNext={goNext}
      />

      {/* 4) Email modal */}
      {showEmailModal && (
        <EmailModal onClose={handleCloseModal} onSend={handleSendEmail} />
      )}
    </div>
  );
}
