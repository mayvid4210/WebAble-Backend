# WebAble Backend

## Start the FastAPI API

From this directory, install the project requirements and Playwright's Chromium browser if needed:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Start the API with:

```powershell
python -m uvicorn webable.api.app:app --reload
```

The health check is available at `http://127.0.0.1:8000/api/health`.

## Analyze a website

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/analyze `
  -H "Content-Type: application/json" `
  -d '{"url":"https://example.com"}'
```

The response has a top-level `report` object containing the URL and final URL, page title, score, severity counts, page structure, findings with WCAG references and affected elements, passed checks, and scan metadata.

## Analysis pipeline

`analyze_website()` captures a compact `PageSnapshot`, runs the registered analyzers in `webable/pipeline.py`, combines their `AnalyzerResult` values, and builds the existing `AuditReport`. Analyzer implementations follow the `Analyzer` protocol in `webable/analyzers/base.py`; current implementations are `AxeAccessibilityAnalyzer`, `PageStructureAnalyzer`, and `VisualAccessibilityAnalyzer`. The visual analyzer reports measurable text contrast issues not already reported by axe and very-small-text readability signals. To add an analyzer, implement that contract and register it in `webable/pipeline.py`. The API and frontend consume the combined report and do not depend on individual analyzer implementations.

## CORS development origins

The API allows `http://localhost:5173` and `http://127.0.0.1:5173` by default for local Vite development. Override the comma-separated origins with `WEBABLE_CORS_ORIGINS`.

## Start the React + Vite frontend

In a second terminal, from the `frontend` directory:

```powershell
Set-Location .\frontend
npm install
npm run dev
```

Vite serves the frontend at `http://localhost:5173` and proxies `/api` requests to `http://127.0.0.1:8000`. Set `VITE_API_BASE_URL` to use a different API base URL, or `VITE_API_PROXY_TARGET` to change the local proxy target (see `frontend/.env.example`).
