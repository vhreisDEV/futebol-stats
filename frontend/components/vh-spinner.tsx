import "./vh-spinner.css";

interface VhSpinnerProps {
  className?: string;
}

export function VhSpinner({ className = "" }: VhSpinnerProps) {
  return (
    <div className={`vh-spinner ${className}`.trim()} role="status" aria-label="Carregando">
      <span className="vh-spinner-label">VH</span>
    </div>
  );
}
