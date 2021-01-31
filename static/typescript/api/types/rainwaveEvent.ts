import Station from "./station";
import RainwaveTime from "./time";

export default interface RainwaveEvent {
  id: number;
  start: RainwaveTime;
  start_actual: RainwaveTime;
  end: RainwaveTime;
  type: "Election" | "OneUpProducer" | "PVPElectionProducer";
  name: string | null;
  sid: Station;
  url: string | null;
  voting_allowed: boolean;
  used: boolean;
  length: number;
  core_event_id: number | null;
}
