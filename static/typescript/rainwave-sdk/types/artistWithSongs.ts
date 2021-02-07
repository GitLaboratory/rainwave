import Album from "./album";
import Artist from "./artist";
import Station from "./station";

interface SongInArtist {
  albums: [Pick<Album, "id" | "name" | "year">];
  cool: boolean;
  disc_number: number | null;
  fave: boolean | null;
  id: number;
  length: number;
  link_text: string | null;
  rating_user: number | null;
  rating: number;
  requestable: boolean;
  sid: Station;
  title: string;
  track_number: number | null;
  url: string | null;
}

export default interface ArtistWithSongs extends Artist {
  all_songs: Record<Station, Record<number, SongInArtist[]>>;
}
