import Station from "./station";
import RainwaveTime from "./time";

interface SearchAlbum {
  id: number;
  name: string;
  cool: boolean;
  rating: number;
  album_name_searchable?: string;
  fave: boolean | null;
  rating_user: number | null;
  rating_complete: boolean | null;
}

interface SearchArtist {
  id: number;
  name: string;
  name_searchable?: string;
}

interface SearchSong {
  id: number;
  length: number;
  origin_sid: Station;
  title: string;
  added_on: RainwaveTime;
  track_number: number | null;
  disc_number: number | null;
  url: string | null;
  link_text: string | null;
  rating: number;
  requestable: boolean;
  cool: boolean;
  cool_end: RainwaveTime;
  artist_parseable?: string;
  rating_user: number | null;
  fave: boolean | null;
  album_name: string;
  album_id: number;
  album_name_searchable?: string;
}

export interface SearchResult {
  albums: SearchAlbum[];
  artists: SearchArtist[];
  songs: SearchSong[];
}
