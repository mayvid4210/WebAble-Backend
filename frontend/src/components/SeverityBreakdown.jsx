const SEVERITIES = [
  ["critical", "Critical"],
  ["serious", "Serious"],
  ["moderate", "Moderate"],
  ["minor", "Minor"],
];

export default function SeverityBreakdown({ counts }) {
  return (
    <section aria-labelledby="severity-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">FINDINGS</p>
          <h2 id="severity-heading">Issue breakdown</h2>
        </div>
      </div>
      <dl className="severity-grid">
        {SEVERITIES.map(([key, label]) => (
          <div className={`severity-card severity-card--${key}`} key={key}>
            <dt>
              <span className="severity-mark" aria-hidden="true" />
              {label}
            </dt>
            <dd>{counts[key]}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
