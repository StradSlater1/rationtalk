import "./NewsForm.css";
import ReviewButton from "../ReviewButton/ReviewButton";
import SectionSelector from "../SectionSelector/SectionSelector";
import ArticleCountSelector from "../ArticleCountSelector/ArticleCountSelector";

interface NewsFormProps {
  selectedSections: string[];
  onToggleSection: (section: string) => void;
  articleCount: number;
  onIncrement: () => void;
  onDecrement: () => void;
  onSubmit: () => void;
}

function NewsForm({
  selectedSections,
  onToggleSection,
  articleCount,
  onIncrement,
  onDecrement,
  onSubmit,
}: NewsFormProps) {
  // e.g. disable button if no section selected
  const isButtonDisabled = selectedSections.length === 0;

  return (
    <form
      className="news-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="section-chooser">
        <label className="section-chooser__label">
          Which sections would you like to read from?
        </label>
        <SectionSelector
          selectedSections={selectedSections}
          onToggleSection={onToggleSection}
        />
      </div>

      <div className="count-chooser">
        <label className="count-chooser__label">
          How many articles would you like to summarize?
        </label>
        <ArticleCountSelector
          count={articleCount}
          onIncrement={onIncrement}
          onDecrement={onDecrement}
        />
      </div>

      <ReviewButton onClick={onSubmit} disabled={isButtonDisabled} />
    </form>
  );
}

export default NewsForm;
