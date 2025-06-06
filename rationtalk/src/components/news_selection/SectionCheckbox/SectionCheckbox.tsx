import "./SectionCheckbox.css";

interface SectionCheckboxProps {
  label: string;
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

function SectionCheckbox({ label, checked, onChange }: SectionCheckboxProps) {
  return (
    <div className="section-checkbox">
      <input
        type="checkbox"
        id={`checkbox-${label}`}
        checked={checked}
        onChange={onChange}
      />
      <label htmlFor={`checkbox-${label}`}>{label}</label>
    </div>
  );
}

export default SectionCheckbox;
