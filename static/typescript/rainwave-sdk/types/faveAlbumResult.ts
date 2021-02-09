import Station from "./station";

export default interface FaveAlbumResult {
  id: number;
  fave: boolean;
  sid: Station;
  success: boolean;
  tl_key: string;
  text: string;
}
