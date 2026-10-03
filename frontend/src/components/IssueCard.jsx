const IMPACT_LABELS = {
  critical: "Critical",
  serious: "Serious",
  moderate: "Moderate",
  minor: "Minor",
};

export default function IssueCard({ finding, index }) {
  const impact = finding.impact?.toLowerCase() || "unknown";
  const label = IMPACT_LABELS[impact] || "Impact not specified";

  return (
    <details className="issue-card">
      <summary className="issue-summary">
        <span className={`impact-badge impact-badge--${impact}`}>{label}</span>
        <span className="issue-title">{finding.title}</span>
        <span className="issue-rule">{finding.rule_id}</span>
        <span className="details-chevron" aria-hidden="true">
          +
        </span>
      </summary>
      <div className="issue-content">
        <p className="issue-description">{finding.description}</p>

        <div className="issue-meta">
          <span>
            <strong>{finding.affected_elements.length}</strong> affected{" "}
            {finding.affected_elements.length === 1 ? "element" : "elements"}
          </span>
          <span>
            Rule <code>{finding.rule_id}</code>
          </span>
        </div>

        {finding.wcag_references.length > 0 && (
          <div className="evidence-block">
            <h3>WCAG references</h3>
            <ul className="tag-list">
              {finding.wcag_references.map((reference) => (
                <li key={reference}>{reference}</li>
              ))}
            </ul>
          </div>
        )}

        {finding.affected_elements.map((element, elementIndex) => (
          <div className="evidence-block" key={`${index}-${elementIndex}`}>
            <h3>
              Affected element
              {element.target.length > 0 && (
                <span className="target-selector">
                  {" "}
                  · {element.target.join(", ")}
                </span>
              )}
            </h3>
            {element.html && (
              <pre className="code-evidence">
                <code>{element.html}</code>
              </pre>
            )}
            {element.failure_summary && (
              <p className="failure-summary">{element.failure_summary}</p>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}
