import Artist from "./artist";
import ElecBlockedBy from "./elecBlockBy";
import SongGroup from "./songGroup";
import Station from "./station";

interface SongWithDetailArtist extends Artist {
  order: number;
}

interface SongWithDetailAlbum {
  id: number;
  rating: number;
  art: string;
  name: string;
  rating_user: number | null;
  rating_complete: boolean | null;
  fave: boolean | null;
}

export default interface SongWithDetail {
  title: string;
  id: number;
  rating: number;
  origin_sid: Station;
  link_text: string | null;
  artist_parseable?: string;
  cool: boolean;
  url: string | null;
  elec_blocked: boolean;
  elec_blocked_by: ElecBlockedBy;
  length: number;
  track_number: number | null;
  disc_number: number | null;
  year: number | null;
  rating_user: number | null;
  fave: boolean | null;
  rating_allowed: boolean;
  sid: Station;
  rating_rank: number;
  request_rank: number;
  request_count: number;
  rating_count: number;
  rating_rank_percentile: number;
  request_rank_percentile: number;
  groups: SongGroup[];
  artists: SongWithDetailArtist[];
  album: [SongWithDetailAlbum];
}
