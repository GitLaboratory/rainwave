import BooleanResult from "./booleanResult";
import Station from "./station";

export default interface FaveAlbumResult extends BooleanResult {
  id: number;
  fave: boolean;
  sid: Station;
}
