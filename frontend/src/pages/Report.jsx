import Brand from "../components/Brand.jsx";
import IssueList from "../components/IssueList.jsx";
import PageStructure from "../components/PageStructure.jsx";
import PassedChecks from "../components/PassedChecks.jsx";
import ScoreCard from "../components/ScoreCard.jsx";
import SeverityBreakdown from "../components/SeverityBreakdown.jsx";

export default function Report({ report, submittedUrl, onNewScan }) {
  return (
    <main className="report-page" id="report">
      <header className="site-header report-header">
        <Brand compact onHome={onNewScan} />
        <button className="button button--quiet" onClick={onNewScan}>
          <span aria-hidden="true">←</span> New scan
        </button>
      </header>

      <div className="report-main">
        <div className="report-breadcrumb">
          <span>ACCESSIBILITY AUDIT</span>
          <span aria-hidden="true">/</span>
          <span>PAGE REPORT</span>
        </div>

        <section className="report-heading" aria-labelledby="report-title">
          <p className="eyebrow">AUDIT REPORT</p>
          <h1 id="report-title">{report.title || "Untitled page"}</h1>
          <a
            className="report-url"
            href={report.final_url || report.url}
            target="_blank"
            rel="noreferrer"
          >
            {report.final_url || report.url}
            <span className="external-link" aria-hidden="true">
              ↗
            </span>
          </a>
          {submittedUrl !== report.url && (
            <p className="submitted-url">Submitted as {submittedUrl}</p>
          )}
        </section>

        <div className="report-summary">
          <ScoreCard score={report.score} />
          <div className="summary-metrics" aria-label="Audit summary">
            <div>
              <span className="summary-number">{report.findings.length}</span>
              <span className="summary-label">Issues found</span>
            </div>
            <div>
              <span className="summary-number">
                {report.passed_checks.length}
              </span>
              <span className="summary-label">Checks passed</span>
            </div>
            <div>
              <span className="summary-number">
                {report.page_structure.images_without_alt}
              </span>
              <span className="summary-label">Missing alt text</span>
            </div>
          </div>
        </div>

        <div className="report-sections">
          <SeverityBreakdown counts={report.severity_counts} />
          <PageStructure structure={report.page_structure} />
          <IssueList findings={report.findings} />
          <PassedChecks checks={report.passed_checks} />
        </div>

        <p className="report-disclaimer">
          This is an automated page-level accessibility audit. A high automated
          score does not guarantee full WCAG conformance or complete
          accessibility.
        </p>
      </div>
      <footer className="site-footer report-footer">
        <span>WebAble</span>
        <span>Evidence first. People always.</span>
      </footer>
    </main>
  );
}
