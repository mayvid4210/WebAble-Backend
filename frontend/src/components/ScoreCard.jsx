export default function ScoreCard({ score }) {
  return (
    <section className="score-card" aria-labelledby="score-heading">
      <div className="score-card-copy">
        <p className="eyebrow">AUTOMATED ACCESSIBILITY SCORE</p>
        <h2
          id="score-heading"
          className="score-value"
          aria-label={`${score} out of 100`}
        >
          {score}
          <span aria-hidden="true">/</span>
          <span className="score-out-of">100</span>
        </h2>
        <p className="score-note">
          A page-level result from automated checks. It does not establish full
          WCAG conformance or complete accessibility.
        </p>
      </div>
      <div
        className="score-meter"
        role="meter"
        aria-label="Automated accessibility score"
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={score}
      >
        <span style={{ width: `${score}%` }} />
      </div>
    </section>
  );
}
