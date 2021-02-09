import Station from "./station";

export default interface FaveSongResult {
  id: number;
  fave: boolean;
  sid: Station;
  success: true;
  tl_key: string;
  text: string;
}
