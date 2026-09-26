export default function ToolCard({ title, description, buttonText, onClick }) {
  return (
    <div className="tool-card card">
      <h3>{title}</h3>
      <p>{description}</p>
      <button className="btn-secondary" onClick={onClick}>{buttonText}</button>
    </div>
  );
}
