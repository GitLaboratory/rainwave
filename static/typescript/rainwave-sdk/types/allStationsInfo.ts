import RainwaveEvent from "./rainwaveEvent";
import Station from "./station";

interface StationInfo {
  title: string;
  album: string;
  art: string | null;
  event_name: string | null;
  event_type: RainwaveEvent["type"];
}

type AllStationsInfo = Record<Station, StationInfo>;

export default AllStationsInfo;
