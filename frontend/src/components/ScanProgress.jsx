export default function ScanProgress() {
  return (
    <div className="scan-progress" role="status" aria-live="polite">
      <span className="loading-indicator" aria-hidden="true" />
      <span>
        <strong>Checking your page</strong>
        <span className="scan-progress-copy">
          Loading the site and running accessibility checks. This can take a
          moment.
        </span>
      </span>
    </div>
  );
}
