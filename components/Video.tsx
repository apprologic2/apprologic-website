"use client";

import { useRef, useState } from "react";

/**
 * Video im Fließtext mit Vorschaubild und großem Abspielknopf.
 * Lädt die Videodatei erst beim Klick (preload="none"); danach übernimmt der
 * Player des Browsers. Kein externer Dienst, keine Cookies.
 */
export default function Video({ src, poster, label }: { src: string; poster?: string; label: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [started, setStarted] = useState(false);

  return (
    <>
      <video ref={ref} src={src} poster={poster} preload="none" playsInline controls={started} aria-label={label} />
      {!started && (
        <button
          type="button"
          className="play"
          aria-label={label}
          onClick={() => { setStarted(true); ref.current?.play(); }}
        >
          <span aria-hidden="true" />
        </button>
      )}
    </>
  );
}
