import { Album } from "./album";
import { ArtistOnSong } from "./artistOnSong";
import { ElectionSongType } from "./electionSongType";
import { SongGroup } from "./songGroup";
import { Station } from "./station";

export interface Song {
  albums: [Pick<Album, "id" | "rating" | "art" | "name" | "rating_user" | "fave">];
  artist_parseable: string;
  artists: ArtistOnSong[];
  cool: boolean;
  disc_number: number | null;
  elec_blocked_by: boolean;
  elec_blocked: boolean;
  elec_request_user_id: number | null;
  elec_request_username: string | null;
  entry_id: number;
  entry_position: number;
  entry_type: ElectionSongType;
  entry_votes: number;
  fave: boolean | null;
  groups: SongGroup[];
  id: number;
  length: number;
  link_text: string | null;
  origin_sid: Station;
  rating_allowed: boolean;
  rating_count: number;
  rating_user: number | null;
  rating: number;
  request_id?: number;
  request_count: number;
  sid: Station;
  title: string;
  track_number: number | null;
  url: string | null;
  year: number | null;
}

export default Song;
