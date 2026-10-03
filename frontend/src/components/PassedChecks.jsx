export default function PassedChecks({ checks }) {
  return (
    <section className="passed-section" aria-labelledby="passed-heading">
      <details className="passed-details">
        <summary>
          <span>
            <span className="eyebrow">AUTOMATED CHECKS</span>
            <span className="passed-title" id="passed-heading">
              What already works
            </span>
          </span>
          <span className="passed-total">
            {checks.length} passed <span aria-hidden="true">+</span>
          </span>
        </summary>
        {checks.length > 0 ? (
          <ul className="passed-list">
            {checks.map((check, index) => (
              <li key={`${check.title}-${index}`}>{check.title}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">No passing checks were returned.</p>
        )}
      </details>
    </section>
  );
}
