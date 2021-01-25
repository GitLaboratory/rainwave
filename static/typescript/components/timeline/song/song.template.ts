import * as FaveTemplate from "components/fave/fave.template";
import * as RatingTemplate from "components/rating/rating.template";
import * as $l from "templateHelpers/gettext";
import * as SongType from "types/song";

interface SongTemplate {
  rootFragment: DocumentFragment;
  cancel: HTMLDivElement;
  voteButtonText: HTMLSpanElement;
  requestDrag: HTMLDivElement;
  art: HTMLDivElement;
  rating: RatingTemplate;
  votes: HTMLSpanElement;
  songFave: FaveTemplate;
  title: HTMLDivElement;
  albumFave: FaveTemplate;
  albumName: HTMLDivElement;
  cooldown: HTMLDivElement;
  root: HTMLDivElement;
}

interface Context {
  song: SongType;
}

export default function song(
  context: Context,
  rootFragment: DocumentFragment = document.createDocumentFragment()
): SongTemplate {
  const C = document.createElement("div");
  C.className = `timeline-song`;
  rootFragment.appendChild(C);
  if (context.song.request_id) {
    const E = document.createElement("div");
    E.className = `timeline-song__cancel`;
    C.appendChild(E);
    const F = document.createElement("span");
    F.className = `timeline-song__cancel__x`;
    E.appendChild(F);
  }
  if (context.song.entry_id) {
    const H = document.createElement("div");
    H.className = `timeline-song__highlight timeline-song__highlight__left timeline-song__highlight timeline-song__highlight__left`;
    C.appendChild(H);
    const I = document.createElement("div");
    I.className = `timeline-song__highlight timeline-song__highlight__right timeline-song__highlight timeline-song__highlight__right`;
    C.appendChild(I);
    const J = document.createElement("div");
    J.className = `timeline-song__highlight timeline-song__highlight__topleft timeline-song__highlight timeline-song__highlight__topleft`;
    C.appendChild(J);
    const K = document.createElement("div");
    K.className = `timeline-song__highlight timeline-song__highlight__topright timeline-song__highlight timeline-song__highlight__topright`;
    C.appendChild(K);
    const L = document.createElement("div");
    L.className = `timeline-song__highlight timeline-song__highlight__bottomleft timeline-song__highlight timeline-song__highlight__bottomleft`;
    C.appendChild(L);
    const M = document.createElement("div");
    M.className = `timeline-song__highlight timeline-song__highlight__bottomright timeline-song__highlight timeline-song__highlight__bottomright`;
    C.appendChild(M);
  }
  if (context.enable_vote_button) {
    const O = document.createElement("div");
    O.className = `timeline-song__vote-button`;
    C.appendChild(O);
    const P = document.createElement("span");
    P.className = `timeline-song__vote-button__text`;
    O.appendChild(P);
    P.appendChild(document.createTextNode($l("vote")));
  }
  const Q = document.createElement("div");
  Q.className = `timeline-song__art-anchor`;
  C.appendChild(Q);
  if (request_id) {
    const S = document.createElement("div");
    S.className = `timeline-song-request-sort-grab`;
    Q.appendChild(S);
    const T = document.createElement("img");
    T.setAttribute("src", /static/4aegims / sort.svg);
    S.appendChild(T);
  }
  const U = document.createElement("div");
  U.className = `timeline-song__art-container`;
  Q.appendChild(U);
  if (show_station_indicator) {
    const W = document.createElement("div");
    W.className = `power_only timeline-song__station-indicator $station_indicator_className power_only timeline-song__station-indicator $station_indicator_className power_only timeline-song__station-indicator $station_indicator_className`;
    U.appendChild(W);
  }
  if (context.song.elec_request_user_id) {
    const Y = document.createElement("div");
    Y.className = `timeline-song__requester $yourRequestClassName timeline-song__requester $yourRequestClassName`;
    U.appendChild(Y);
    if (!context.MOBILE) {
      const a = document.createElement("a");
      a.href = "#!/listener/{{ elec_request_user_id }}";
      Y.appendChild(a);
      a.appendChild(document.createTextNode(context.song.elec_request_username));
    } else {
      Y.appendChild(document.createTextNode(context.song.elec_request_username));
    }
    const c = document.createElement("div");
    c.className = `timeline-song__request-indicator $yourRequestIndicatorClassName timeline-song__request-indicator $yourRequestIndicatorClassName`;
    U.appendChild(c);
    if (context.yourRequest) {
      c.appendChild(document.createTextNode($l("timeline_art__request_indicator")));
    } else {
      c.appendChild(
        document.createTextNode($l("timeline_art__your_request_indicator"))
      );
    }
  }
  const f = document.createElement("div");
  f.className = `timeline-song__content`;
  C.appendChild(f);
  const g = rating<Context>(context, f);
  if (context.song.entry_id) {
    const i = document.createElement("div");
    i.className = `timeline-song__content__entry-votes`;
    f.appendChild(i);
    const j = document.createElement("span");
    i.appendChild(j);
  }
  const k = fave<Context["$song"]>(context.$song, f);
  const l = document.createElement("div");
  l.className = `timeline-song__content__title`;
  l.setAttribute("title", context.song.title);
  f.appendChild(l);
  l.appendChild(document.createTextNode(context.song.title));
  if (!Sizing.simple) {
    const n = document.createElement("albumrating");
    n.setAttribute("context", context.song.albums[0]);
    f.appendChild(n);
  }
  const o = fave<Context["$song.albums[0]"]>(context.$song.albums[0], f);
  const p = document.createElement("div");
  p.className = `timeline-song__content__album`;
  p.setAttribute("title", context.song.albums[0].name);
  f.appendChild(p);
  const q = document.createElement("a");
  q.href = "context.albumLink";
  p.appendChild(q);
  q.appendChild(document.createTextNode(context.song.albums[0].name));
  if (context.song.request_id) {
    const s = document.createElement("div");
    s.className = `timeline-song__content__cooldown-info`;
    f.appendChild(s);
  } else {
    const u = document.createElement("div");
    u.className = `timeline-song__content__artist`;
    f.appendChild(u);
    const v = document.createElement("foreach");
    v.setAttribute("array", context.song.artists);
    u.appendChild(v);
    const w = document.createElement("a");
    w.href = "context.href";
    v.appendChild(w);
    w.appendChild(document.createTextNode(name));
    const x = document.createElement("span");
    x.className = `timeline-song__content__artist__comma`;
    v.appendChild(x);
    if (context.song.url) {
      const z = document.createElement("div");
      z.className = `timeline-song__content__song_link`;
      f.appendChild(z);
      const zA = document.createElement("a");
      zA.className = `timeline-song__content__song_link__link`;
      zA.href = "context.song.url";
      zA.setAttribute("target", _blank);
      z.appendChild(zA);
      zA.appendChild(document.createTextNode(context.song.link_text));
    }
  }
  const result: SongTemplate = {
    rootFragment,
    cancel: E,
    voteButtonText: P,
    requestDrag: S,
    art: U,
    rating: g,
    votes: j,
    songFave: k,
    title: l,
    albumFave: o,
    albumName: p,
    cooldown: s,
    root: C,
  };
  return result;
}
