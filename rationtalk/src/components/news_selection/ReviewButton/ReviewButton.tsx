import "./ReviewButton.css";

interface ReviewButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

function ReviewButton({ onClick, disabled = false }: ReviewButtonProps) {
  return (
    <button
      type="submit"
      className="review-button"
      onClick={onClick}
      disabled={disabled}
    >
      Review news
    </button>
  );
}

export default ReviewButton;
