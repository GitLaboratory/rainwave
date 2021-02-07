import Album from "./album";
import Song from "./song";
import SongGroup from "./songGroup";

export default interface AlbumWithDetail extends Album {
  genres: SongGroup[];
  rating_complete: boolean;
  rating_rank: number;
  rating_rank_percentile: number;
  request_count: number;
  request_rank: number;
  request_rank_percentile: number;
  rating_histogram: Record<string, number>;
  songs: Song[];
}
