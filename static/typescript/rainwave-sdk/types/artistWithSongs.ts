import Artist from "./artist";
import { SongBase } from "./songBase";
import Station from "./station";

interface SongInArtist extends Omit<SongBase, "artists"> {
  cool: boolean;
  requestable: boolean;
  sid: Station;
}

export default interface ArtistWithSongs extends Artist {
  all_songs: Record<Station, Record<number, SongInArtist[]>>;
}
