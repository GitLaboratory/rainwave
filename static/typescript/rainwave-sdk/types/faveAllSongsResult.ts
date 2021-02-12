import BooleanResult from "./booleanResult";
import Station from "./station";

export default interface FaveAllSongsResult extends BooleanResult {
  song_ids: number[];
  fave: boolean;
  sid: Station;
}
