import Artist from "./artist";

export interface ArtistOnSong extends Artist {
  order: number;
}

export default ArtistOnSong;
