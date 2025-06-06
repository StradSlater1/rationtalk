import SectionCheckbox from "../SectionCheckbox/SectionCheckbox";
import "./SectionSelector.css";

interface SectionSelectorProps {
  selectedSections: string[];
  onToggleSection: (section: string) => void;
}

function SectionSelector({
  selectedSections,
  onToggleSection,
}: SectionSelectorProps) {
  const availableSections = [
    "World",
    "U.S.",
    "Technology",
    "Business",
    "Science",
    "Entertainment",
    "Health",
    "Sports",
  ];

  return (
    <div className="section-selector">
      {availableSections.map((section) => (
        <SectionCheckbox
          key={section}
          label={section}
          checked={selectedSections.includes(section)}
          onChange={() => onToggleSection(section)}
        />
      ))}
    </div>
  );
}

export default SectionSelector;
