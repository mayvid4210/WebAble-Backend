import IssueCard from "./IssueCard.jsx";

export default function IssueList({ findings }) {
  return (
    <section aria-labelledby="findings-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">DETAILED RESULTS</p>
          <h2 id="findings-heading">What WebAble noticed</h2>
        </div>
        <span className="section-count">
          {findings.length} {findings.length === 1 ? "issue" : "issues"}
        </span>
      </div>
      {findings.length === 0 ? (
        <p className="empty-state">
          No violations were detected by the automated accessibility audit.
        </p>
      ) : (
        <div className="issue-list">
          {findings.map((finding, index) => (
            <IssueCard
              finding={finding}
              index={index}
              key={`${finding.rule_id}-${index}`}
            />
          ))}
        </div>
      )}
    </section>
  );
}
