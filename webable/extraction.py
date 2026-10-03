"""Extraction of the existing page-level structure statistics."""

from playwright.sync_api import Page

from webable.models import PageStructure, VisualTextSample

MAX_VISUAL_TEXT_SAMPLES = 300
MAX_TEXT_SAMPLE_LENGTH = 160
MAX_HTML_SAMPLE_LENGTH = 500

_VISUAL_TEXT_SAMPLE_SCRIPT = """
() => {
  const elements = Array.from(document.body?.querySelectorAll("*") ?? []);
  const samples = [];

  function colorParts(value) {
    const match = value.match(
      /^rgba?\\(\\s*([\\d.]+)[, ]+([\\d.]+)[, ]+([\\d.]+)(?:\\s*[,/]\\s*([\\d.]+%?))?\\s*\\)$/i
    );
    if (!match) return null;
    let alpha = match[4] === undefined ? 1 : parseFloat(match[4]);
    if (match[4]?.endsWith("%")) alpha /= 100;
    return [
      Number(match[1]),
      Number(match[2]),
      Number(match[3]),
      Math.min(1, Math.max(0, alpha)),
    ];
  }

  function selectorFor(element) {
    if (element.id) return `#${CSS.escape(element.id)}`;
    const parts = [];
    let current = element;
    while (current && current !== document.body && parts.length < 6) {
      let part = current.localName;
      if (!part) break;
      const siblings = current.parentElement
        ? Array.from(current.parentElement.children).filter(
            (sibling) => sibling.localName === current.localName
          )
        : [];
      if (siblings.length > 1) {
        part += `:nth-of-type(${siblings.indexOf(current) + 1})`;
      }
      parts.unshift(part);
      current = current.parentElement;
      if (parts.join(" ").length > 180) break;
    }
    return parts.length ? `body > ${parts.join(" > ")}` : "body";
  }

  for (const element of elements) {
    const ownText = Array.from(element.childNodes)
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.textContent ?? "")
      .join(" ")
      .replace(/\\s+/g, " ")
      .trim();
    if (!ownText || element.closest('[aria-hidden="true"]')) continue;

    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    if (
      style.display === "none" ||
      style.visibility === "hidden" ||
      style.visibility === "collapse" ||
    Number(style.opacity) === 0 ||
    rect.width <= 0 ||
      rect.height <= 0
    ) continue;

    let opacity = 1;
    let effectiveBackground = [255, 255, 255];
    let backgroundKnown = true;
    let current = element;
    const ancestors = [];
    const styleChain = [];
    while (current && current.nodeType === Node.ELEMENT_NODE) {
      const currentStyle = getComputedStyle(current);
      const currentOpacity = Number(currentStyle.opacity);
      opacity *= currentOpacity;
      if (currentOpacity !== 1) backgroundKnown = false;
      styleChain.push(currentStyle);
      if (currentStyle.backgroundImage !== "none") {
        backgroundKnown = false;
      }
      if (current !== element && ancestors.length < 5) {
        ancestors.push(selectorFor(current));
      }
      current = current.parentElement;
    }
    if (opacity === 0) continue;
    for (const currentStyle of styleChain.reverse()) {
      const background = colorParts(currentStyle.backgroundColor);
      if (background) {
        const alpha = background[3];
        effectiveBackground = effectiveBackground.map(
          (channel, index) =>
            background[index] * alpha + channel * (1 - alpha)
        );
      }
    }

    const foreground = colorParts(style.color);
    let foregroundColor = style.color;
    if (foreground && opacity === 1) {
      const alpha = foreground[3] * opacity;
      const flattenedForeground = foreground.slice(0, 3).map(
        (channel, index) =>
          channel * alpha + effectiveBackground[index] * (1 - alpha)
      );
      foregroundColor = `rgb(${flattenedForeground
        .map((channel) => Math.round(channel))
        .join(", ")})`;
    }

    const flattenedBackground = `rgb(${effectiveBackground
      .map((channel) => Math.round(channel))
      .join(", ")})`;
    const fontSize = Number.parseFloat(style.fontSize);
    samples.push({
      selector: selectorFor(element),
      ancestor_selectors: ancestors,
      text: ownText.slice(0, 160),
      tag: element.localName,
      foreground_color: foregroundColor,
      background_color: backgroundKnown ? flattenedBackground : null,
      font_size_px: Number.isFinite(fontSize) ? fontSize : null,
      font_weight: style.fontWeight,
      html: element.outerHTML.slice(0, 500),
    });
    if (samples.length >= 300) break;
  }
  return samples;
}
"""


def extract_page_structure(page: Page) -> PageStructure:
    return PageStructure(
        title=page.title(),
        final_url=page.url,
        links=page.locator("a").count(),
        images=page.locator("img").count(),
        buttons=page.locator("button").count(),
        forms=page.locator("form").count(),
        inputs=page.locator("input").count(),
        headings=page.locator("h1, h2, h3, h4, h5, h6").count(),
        images_without_alt=page.locator("img:not([alt])").count(),
    )


def extract_visual_text_samples(page: Page) -> list[VisualTextSample]:
    raw_samples = page.evaluate(_VISUAL_TEXT_SAMPLE_SCRIPT)
    if not isinstance(raw_samples, list):
        return []

    samples: list[VisualTextSample] = []
    for raw in raw_samples[:MAX_VISUAL_TEXT_SAMPLES]:
        if not isinstance(raw, dict):
            continue
        selector = raw.get("selector")
        text = raw.get("text")
        tag = raw.get("tag")
        foreground_color = raw.get("foreground_color")
        if not all(
            isinstance(value, str)
            for value in (selector, text, tag, foreground_color)
        ):
            continue
        raw_ancestors = raw.get("ancestor_selectors", [])
        ancestors = (
            [entry for entry in raw_ancestors if isinstance(entry, str)][:5]
            if isinstance(raw_ancestors, list)
            else []
        )
        background_color = raw.get("background_color")
        font_size_px = raw.get("font_size_px")
        font_weight = raw.get("font_weight")
        html = raw.get("html")
        samples.append(
            VisualTextSample(
                selector=selector[:200],
                ancestor_selectors=ancestors,
                text=text[:MAX_TEXT_SAMPLE_LENGTH],
                tag=tag[:30],
                foreground_color=foreground_color[:80],
                background_color=(
                    background_color[:80]
                    if isinstance(background_color, str)
                    else None
                ),
                font_size_px=(
                    float(font_size_px)
                    if isinstance(font_size_px, (int, float))
                    and font_size_px > 0
                    else None
                ),
                font_weight=(
                    font_weight
                    if isinstance(font_weight, (int, str))
                    else "normal"
                ),
                html=html[:MAX_HTML_SAMPLE_LENGTH]
                if isinstance(html, str)
                else "",
            )
        )
    return samples
