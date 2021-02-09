import Album from "./album";
import Station from "./station";

interface GroupSong {
  id: number;
  title: string;
  rating: number;
  requestable: boolean;
  length: number;
  disc_number: number | null;
  track_number: number | null;
  cool: boolean;
  cool_end: number;
  url: string | null;
  link_text: string | null;
  artist_parseable: string;
  rating_user: string;
  fave: boolean;
  albums: Album[];
}

export default interface GroupWithDetail {
  id: number;
  name: string;
  all_songs_for_sid: Record<number, Record<Station, GroupSong>>;
}
