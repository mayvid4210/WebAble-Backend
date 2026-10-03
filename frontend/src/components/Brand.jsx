export default function Brand({ compact = false, onHome }) {
  return (
    <a
      className={`brand${compact ? " brand--compact" : ""}`}
      href="#home"
      aria-label="WebAble home"
      onClick={
        onHome
          ? (event) => {
              event.preventDefault();
              onHome();
            }
          : undefined
      }
    >
      <span className="brand-mark" aria-hidden="true">
        W
      </span>
      <span>WebAble</span>
      <span className="brand-period" aria-hidden="true">
        .
      </span>
    </a>
  );
}
