import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Link from "next/link";
import ContactForm from "./ContactForm";
import Zoomable from "./Zoomable";
import Video from "./Video";

/**
 * Rendert den Markdown-Text einer Seite.
 *
 * Neben normalem Markdown gibt es eigene Blöcke (als Code-Fences):
 *
 * ```tiles            Kacheln. Ein Absatz je Kachel: erste Zeile Titel,
 * Titel               dann Text, optional letzte Zeile "-> /pfad/ Linktext".
 * Text der Kachel
 * -> /funktionen/ Mehr
 * ```
 *
 * ```numbers          Große Zahlen: "Zahl | Erläuterung", eine je Zeile
 * −20 % | Serviceanfragen ...
 * ```
 *
 * ```cta              Abschlussblock: erste Zeile Überschrift, dann Text,
 * Überschrift         Buttons als "-> /pfad/ Beschriftung" (erster = primär)
 * -> /kontakt/ Demo anfragen
 * ```
 *
 * ```image            Bild: erste Zeile Pfad (Datei in public/), danach Alt-Text.
 * /bilder/datei.svg   Ohne Pfad erscheint ein Platzhalter mit dem Text als Beschreibung.
 *                     Optional nach dem Pfad eine Variante, z. B. "logos" (weiß, mit Innenabstand).
 * Screenshot der Maschinenliste
 * ```
 *
 * ```video            Video: erste Zeile Pfad zur MP4 (in public/), optional dahinter
 * /video/datei.mp4 /video/datei.jpg   das Vorschaubild. Danach die Beschreibung (für Screenreader).
 * Beschreibung des Videos
 * ```
 *
 * ```form             Kontaktformular
 * ```
 */

const LINK = /^->\s*(\S+)\s+(.+)$/;
const IMAGE_SRC = /^\/\S+\.(svg|png|jpe?g|webp|avif|gif)$/i;
const VIDEO_SRC = /^\/\S+\.(mp4|webm)$/i;

function Tiles({ src }: { src: string }) {
  const blocks = src.trim().split(/\n\s*\n/);
  return (
    <div className="tiles">
      {blocks.map((b, i) => {
        const lines = b.trim().split("\n");
        const title = lines[0];
        const link = lines.at(-1)?.match(LINK);
        const text = (link ? lines.slice(1, -1) : lines.slice(1)).join(" ");
        const inner = (
          <>
            <b>{title}</b>
            {text}
            {link && <span className="more">{link[2]} →</span>}
          </>
        );
        return link ? (
          <Link key={i} className="tile" href={link[1]}>{inner}</Link>
        ) : (
          <div key={i} className="tile">{inner}</div>
        );
      })}
    </div>
  );
}

function Image({ src }: { src: string }) {
  const [first, ...rest] = src.trim().split("\n");
  const [path, variant] = first.trim().split(/\s+/);
  if (!IMAGE_SRC.test(path)) return <div className="img">{src.trim()}</div>;
  return (
    <figure className={`figure${variant ? ` figure-${variant}` : ""}`}>
      {variant === "logos"
        ? <img src={path} alt={rest.join(" ").trim()} loading="lazy" />
        : <Zoomable src={path} alt={rest.join(" ").trim()} />}
    </figure>
  );
}

function VideoBlock({ src }: { src: string }) {
  const [first, ...rest] = src.trim().split("\n");
  const [path, poster] = first.trim().split(/\s+/);
  if (!VIDEO_SRC.test(path)) return <div className="img">{src.trim()}</div>;
  return (
    <figure className="figure figure-video">
      <Video src={path} poster={poster && IMAGE_SRC.test(poster) ? poster : undefined} label={rest.join(" ").trim()} />
    </figure>
  );
}

function Numbers({ src }: { src: string }) {
  return (
    <div className="numbers">
      {src.trim().split("\n").map((line, i) => {
        const [n, ...rest] = line.split("|");
        return (
          <div key={i} className="num">
            <strong>{n.trim()}</strong>
            <span>{rest.join("|").trim()}</span>
          </div>
        );
      })}
    </div>
  );
}

function Cta({ src }: { src: string }) {
  const lines = src.trim().split("\n");
  const links = lines.filter((l) => LINK.test(l)).map((l) => l.match(LINK)!);
  const text = lines.filter((l) => !LINK.test(l));
  return (
    <div className="next">
      <h2>{text[0]}</h2>
      {text.slice(1).map((t, i) => <p key={i}>{t}</p>)}
      <div className="btns">
        {links.map((l, i) => (
          <Link key={i} className={`btn${i === 0 ? " primary" : ""}`} href={l[1]}>{l[2]}</Link>
        ))}
      </div>
    </div>
  );
}

export default function Markdown({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        a: ({ href, children }) =>
          href?.startsWith("/") ? <Link href={href}>{children}</Link> : <a href={href}>{children}</a>,
        table: ({ children }) => <div className="tw"><table>{children}</table></div>,
        code: ({ className, children }) => {
          const lang = className?.replace("language-", "");
          const src = String(children);
          if (lang === "tiles") return <Tiles src={src} />;
          if (lang === "numbers") return <Numbers src={src} />;
          if (lang === "cta") return <Cta src={src} />;
          if (lang === "image") return <Image src={src} />;
          if (lang === "video") return <VideoBlock src={src} />;
          if (lang === "form") return <ContactForm />;
          return <code className={className}>{children}</code>;
        },
        // Code-Fences nicht in <pre> einpacken, damit die Blöcke oben frei stehen
        pre: ({ children }) => <>{children}</>,
      }}
    >
      {children}
    </ReactMarkdown>
  );
}
