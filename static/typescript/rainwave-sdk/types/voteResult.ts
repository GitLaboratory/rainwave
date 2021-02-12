import BooleanResult from "./booleanResult";

export default interface VoteResult extends BooleanResult {
  elec_id: number;
  entry_id: number;
}
