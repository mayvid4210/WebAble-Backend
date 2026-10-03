const METRICS = [
  ["links", "Links"],
  ["images", "Images"],
  ["buttons", "Buttons"],
  ["forms", "Forms"],
  ["inputs", "Inputs"],
  ["headings", "Headings"],
  ["images_without_alt", "Images without alt text"],
  ["elements_scanned", "Elements scanned"],
];

export default function PageStructure({ structure }) {
  return (
    <section aria-labelledby="structure-heading">
      <div className="section-heading">
        <div>
          <p className="eyebrow">PAGE OVERVIEW</p>
          <h2 id="structure-heading">Page structure</h2>
        </div>
      </div>
      <dl className="structure-grid">
        {METRICS.map(([key, label]) => (
          <div className="structure-item" key={key}>
            <dt>{label}</dt>
            <dd>{structure[key]}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
