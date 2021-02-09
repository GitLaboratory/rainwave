import Station from "./station";

export default interface FaveAllSongsResult {
  song_ids: number[];
  fave: boolean;
  sid: Station;
  success: boolean;
  tl_key: string;
  text: string;
}
