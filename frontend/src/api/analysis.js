const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "/api"
).replace(/\/+$/, "");

export async function analyzeWebsite(url, { signal } = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
      signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }
    throw new Error(
      "WebAble could not reach the analysis service. Check that the API is running and try again.",
    );
  }

  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error("The analysis service returned an unreadable response.");
  }

  if (!response.ok) {
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : "The analysis could not be completed.";
    throw new Error(detail);
  }

  if (!body.report || typeof body.report !== "object") {
    throw new Error("The analysis service returned an incomplete report.");
  }

  return body.report;
}
