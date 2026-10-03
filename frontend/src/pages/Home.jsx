import { useState } from "react";
import { analyzeWebsite } from "../api/analysis.js";
import Brand from "../components/Brand.jsx";
import ScanForm from "../components/ScanForm.jsx";
import ScanProgress from "../components/ScanProgress.jsx";

export default function Home({ onReport }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze(url) {
    setLoading(true);
    setError("");
    try {
      const report = await analyzeWebsite(url);
      onReport(report);
    } catch (scanError) {
      setError(scanError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="home-page" id="home">
      <header className="site-header">
        <Brand />
        <span className="header-caption">ACCESSIBILITY, UNDERSTOOD</span>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow hero-eyebrow">
            A CLEARER VIEW OF YOUR WEBSITE
          </p>
          <h1 id="hero-title">
            See your website
            <br />
            <span>through every user.</span>
          </h1>
          <p className="hero-description">
            Start with an automated accessibility scan. Explore measurable
            findings, understand what was checked, and see where barriers may
            exist.
          </p>
        </div>

        <div className="scan-panel">
          <ScanForm onSubmit={handleAnalyze} loading={loading} />
          {loading && <ScanProgress />}
          {error && (
            <div className="error-message" role="alert" aria-live="assertive">
              <span className="error-symbol" aria-hidden="true">
                !
              </span>
              <span>
                <strong>We couldn’t complete this scan.</strong>
                <span>{error}</span>
              </span>
            </div>
          )}
        </div>

        <div className="hero-footnote">
          <span aria-hidden="true" className="footnote-line" />
          <p>
            Automated checks are a starting point—not a substitute for human
            evaluation.
          </p>
        </div>
      </section>

      <footer className="site-footer">
        <span>WebAble</span>
        <span>One page at a time.</span>
      </footer>
    </main>
  );
}
