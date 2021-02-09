import RainwaveTime from "./time";

interface PlaybackHistoryEntry {
  album_id: number;
  album_name: string;
  artist_parseable: string;
  fave: boolean | null;
  id: number;
  rating: number;
  rating_user: number | null;
  song_played_at: RainwaveTime;
  title: string;
}

type PlaybackHistory = PlaybackHistoryEntry[];

export default PlaybackHistory;
