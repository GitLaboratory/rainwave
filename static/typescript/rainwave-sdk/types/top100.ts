import Station from "./station";

interface Top100Song {
  album_name: string;
  id: number;
  origin_sid: Station;
  song_rating: number;
  song_rating_count: number;
  title: string;
}

type Top100 = Top100Song[];

export default Top100;
