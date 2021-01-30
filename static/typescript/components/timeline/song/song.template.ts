import $l from "templateHelpers/gettext";
import rating, { RatingTemplate } from "components/rating/rating.template";
import fave, { FaveTemplate } from "components/fave/fave.template";
import Song from "types/song";
import Sizing from "types/sizing";

export interface SongTemplate {
  rootFragment: HTMLElement | DocumentFragment;
  cancel: HTMLDivElement | undefined;
  voteButtonText: HTMLSpanElement | undefined;
  requestDrag: HTMLDivElement | undefined;
  art: HTMLDivElement;
  rating: RatingTemplate;
  votes: HTMLSpanElement | undefined;
  songFave: FaveTemplate;
  title: HTMLDivElement;
  albumFave: FaveTemplate;
  albumName: HTMLDivElement;
  cooldown: HTMLDivElement | undefined;
  root: HTMLDivElement;
}

interface Context {
  song: Song;
  enableVoteButton: boolean;
  showStationIndicator: boolean;
  MOBILE: boolean;
  yourRequest: boolean;
  sizing: Sizing;
  stationIndicatorClassname: string;
  yourRequestClassName: string;
  yourRequestIndicatorClassName: string;
}

export default function song(
  context: Context,
  rootFragment:
    | HTMLElement
    | DocumentFragment = document.createDocumentFragment()
): SongTemplate {
  let N: HTMLDivElement | undefined;
  let Y: HTMLSpanElement | undefined;
  let b: HTMLDivElement | undefined;
  let d: HTMLDivElement;
  let q: RatingTemplate;
  let t: HTMLSpanElement | undefined;
  let u: FaveTemplate;
  let v: HTMLDivElement;
  let y: FaveTemplate;
  let z: HTMLDivElement;
  let zC: HTMLDivElement | undefined;
  let L: HTMLDivElement;
  L = document.createElement("div");
  L.className = `timeline-song`;
  rootFragment.appendChild(L);
  if (context.song.request_id) {
    N = document.createElement("div");
    N.className = `timeline-song__cancel`;
    L.appendChild(N);
    const O = document.createElement("span");
    O.className = `timeline-song__cancel__x`;
    N.appendChild(O);
    O.appendChild(document.createTextNode(`x`));
  }
  if (context.song.entry_id) {
    const Q = document.createElement("div");
    Q.className = `timeline-song__highlight timeline-song__highlight__left`;
    L.appendChild(Q);
    const R = document.createElement("div");
    R.className = `timeline-song__highlight timeline-song__highlight__right`;
    L.appendChild(R);
    const S = document.createElement("div");
    S.className = `timeline-song__highlight timeline-song__highlight__topleft`;
    L.appendChild(S);
    const T = document.createElement("div");
    T.className = `timeline-song__highlight timeline-song__highlight__topright`;
    L.appendChild(T);
    const U = document.createElement("div");
    U.className = `timeline-song__highlight timeline-song__highlight__bottomleft`;
    L.appendChild(U);
    const V = document.createElement("div");
    V.className = `timeline-song__highlight timeline-song__highlight__bottomright`;
    L.appendChild(V);
  }
  if (context.enableVoteButton) {
    const X = document.createElement("div");
    X.className = `timeline-song__vote-button`;
    L.appendChild(X);
    Y = document.createElement("span");
    Y.className = `timeline-song__vote-button__text`;
    X.appendChild(Y);
    Y.appendChild(document.createTextNode(`${$l("vote")}`));
  }
  const Z = document.createElement("div");
  Z.className = `timeline-song__art-anchor`;
  L.appendChild(Z);
  if (context.song.request_id) {
    b = document.createElement("div");
    b.className = `timeline-song__request-sort-grab`;
    Z.appendChild(b);
    const c = document.createElement("img");
    c.setAttribute("src", `/static/images4/sort.svg`);
    b.appendChild(c);
  }
  d = document.createElement("div");
  d.className = `timeline-song__art-container`;
  Z.appendChild(d);
  if (context.showStationIndicator) {
    const f = document.createElement("div");
    f.className = `power_only timeline-song__station-indicator ${context.stationIndicatorClassname}`;
    d.appendChild(f);
  }
  if (context.song.elec_request_user_id) {
    if (context.song.elec_request_username) {
      const i = document.createElement("div");
      i.className = `timeline-song__requester ${context.yourRequestClassName}`;
      d.appendChild(i);
      if (!context.MOBILE) {
        const k = document.createElement("a");
        k.href = `#!/listener/${context.song.elec_request_user_id}`;
        i.appendChild(k);
        k.appendChild(
          document.createTextNode(`${context.song.elec_request_username}`)
        );
      } else {
        i.appendChild(
          document.createTextNode(`${context.song.elec_request_username}`)
        );
      }
      const m = document.createElement("div");
      m.className = `timeline-song__request-indicator ${context.yourRequestIndicatorClassName}`;
      d.appendChild(m);
      if (context.yourRequest) {
        m.appendChild(
          document.createTextNode(`${$l("timeline_art__request_indicator")}`)
        );
      } else {
        m.appendChild(
          document.createTextNode(
            `${$l("timeline_art__your_request_indicator")}`
          )
        );
      }
    }
  }
  const p = document.createElement("div");
  p.className = `timeline-song__content`;
  L.appendChild(p);
  q = rating(context, p);
  if (context.song.entry_id) {
    const s = document.createElement("div");
    s.className = `timeline-song__content__entry-votes`;
    p.appendChild(s);
    t = document.createElement("span");
    s.appendChild(t);
  }
  u = fave(context.song, p);
  v = document.createElement("div");
  v.className = `timeline-song__content__title`;
  v.setAttribute("title", `context.song.title`);
  p.appendChild(v);
  v.appendChild(document.createTextNode(`${context.song.title}`));
  if (!context.sizing.simple) {
    const x = document.createElement("albumrating");
    x.setAttribute("context", `context.song.albums[0]`);
    p.appendChild(x);
  }
  y = fave(context.song.albums[0], p);
  z = document.createElement("div");
  z.className = `timeline-song__content__album`;
  z.setAttribute("title", `context.song.albums[0].name`);
  p.appendChild(z);
  const zA = document.createElement("a");
  zA.href = `#!/album/${context.song.albums[0].id}`;
  z.appendChild(zA);
  zA.appendChild(document.createTextNode(`${context.song.albums[0].name}`));
  if (context.song.request_id) {
    zC = document.createElement("div");
    zC.className = `timeline-song__content__cooldown-info`;
    p.appendChild(zC);
  } else {
    const zE = document.createElement("div");
    zE.className = `timeline-song__content__artist`;
    p.appendChild(zE);
    context.song.artists.forEach((context) => {
      const zG = document.createElement("a");
      zG.href = `#!/artist/${context.id}`;
      zE.appendChild(zG);
      zG.appendChild(document.createTextNode(`${context.name}`));
      const zH = document.createElement("span");
      zH.className = `timeline-song__content__artist__comma`;
      zE.appendChild(zH);
      zH.appendChild(document.createTextNode(`,`));
    });
    if (context.song.url) {
      if (context.song.link_text) {
        const zK = document.createElement("div");
        zK.className = `timeline-song__content__song_link`;
        p.appendChild(zK);
        const zL = document.createElement("a");
        zL.className = `timeline-song__content__song_link__link`;
        zL.href = `${context.song.url}`;
        zL.setAttribute("target", `_blank`);
        zK.appendChild(zL);
        zL.appendChild(document.createTextNode(`${context.song.link_text}`));
      }
    }
  }
  const result: SongTemplate = {
    rootFragment,
    cancel: N,
    voteButtonText: Y,
    requestDrag: b,
    art: d,
    rating: q,
    votes: t,
    songFave: u,
    title: v,
    albumFave: y,
    albumName: z,
    cooldown: zC,
    root: L,
  };
  return result;
}
