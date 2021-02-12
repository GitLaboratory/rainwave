import BooleanResult from "./booleanResult";
import Station from "./station";

export default interface FaveSongResult extends BooleanResult {
  id: number;
  fave: boolean;
  sid: Station;
}
