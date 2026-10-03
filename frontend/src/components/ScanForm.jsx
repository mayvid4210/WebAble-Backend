import { useState } from "react";

export default function ScanForm({ onSubmit, loading }) {
  const [url, setUrl] = useState("");
  const [validationMessage, setValidationMessage] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const value = url.trim();
    if (!value) {
      setValidationMessage("Enter a website address to start the scan.");
      return;
    }

    const normalizedValue = /^[a-z][a-z\d+.-]*:\/\//i.test(value)
      ? value
      : `https://${value}`;
    let parsedUrl;
    try {
      parsedUrl = new URL(normalizedValue);
    } catch {
      setValidationMessage("Enter a valid HTTP or HTTPS website address.");
      return;
    }
    if (
      !["http:", "https:"].includes(parsedUrl.protocol) ||
      !parsedUrl.hostname ||
      parsedUrl.username ||
      parsedUrl.password
    ) {
      setValidationMessage("Enter a valid HTTP or HTTPS website address.");
      return;
    }

    setValidationMessage("");
    onSubmit(parsedUrl.href);
  }

  return (
    <form className="scan-form" onSubmit={handleSubmit} noValidate>
      <label htmlFor="website-url">Website address</label>
      <div className="scan-form-row">
        <input
          id="website-url"
          name="url"
          type="text"
          inputMode="url"
          autoComplete="url"
          placeholder="https://example.com"
          value={url}
          onChange={(event) => {
            setUrl(event.target.value);
            if (validationMessage) setValidationMessage("");
          }}
          aria-describedby={
            validationMessage ? "url-hint url-error" : "url-hint"
          }
          aria-invalid={Boolean(validationMessage)}
          disabled={loading}
        />
        <button className="button button--primary" type="submit" disabled={loading}>
          {loading ? "Scanning…" : "Analyze website"}
          {!loading && (
            <span aria-hidden="true" className="button-arrow">
              →
            </span>
          )}
        </button>
      </div>
      <p className="field-hint" id="url-hint">
        A single-page automated accessibility audit. No account required.
      </p>
      {validationMessage && (
        <p className="field-error" id="url-error" role="alert">
          {validationMessage}
        </p>
      )}
    </form>
  );
}
