// src/components/ArticleCountSelector.tsx
import "./ArticleCountSelector.css";

interface articleCountSelectorProps {
  count: number;
  onIncrement: () => void;
  onDecrement: () => void;
}

function ArticleCountSelector({
  count,
  onIncrement,
  onDecrement,
}: articleCountSelectorProps) {
  return (
    <div className="article-count-selector">
      <button
        type="button"
        onClick={onDecrement}
        disabled={count <= 1}
        className="decrement-btn"
      >
        –
      </button>

      <span className="article-count-selector__value">{count}</span>

      <button
        type="button"
        className="increment-btn"
        onClick={() => {
          if (count < 10) {
            onIncrement();
          }
        }}
        disabled={count >= 10}
      >
        +
      </button>
    </div>
  );
}

export default ArticleCountSelector;
