import Artist from "./artist";

export default interface ArtistInLibrary extends Artist {
  song_count: number;
}
