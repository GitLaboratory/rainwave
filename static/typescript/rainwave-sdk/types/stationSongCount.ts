import Station from "./station";

interface StationSongCountByStation {
  sid: Station;
  song_count: number;
}

type StationSongCount = StationSongCountByStation[];

export default StationSongCount;
