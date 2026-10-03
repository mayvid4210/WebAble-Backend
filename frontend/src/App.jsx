import { useState } from "react";
import Home from "./pages/Home.jsx";
import Report from "./pages/Report.jsx";

export default function App() {
  const [report, setReport] = useState(null);
  const [submittedUrl, setSubmittedUrl] = useState("");

  function showReport(nextReport) {
    setReport(nextReport);
    setSubmittedUrl(nextReport.url);
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  function returnHome() {
    setReport(null);
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  if (report) {
    return (
      <Report
        report={report}
        submittedUrl={submittedUrl}
        onNewScan={returnHome}
      />
    );
  }

  return <Home onReport={showReport} />;
}
