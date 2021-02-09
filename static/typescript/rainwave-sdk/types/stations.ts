import Relays from "./relays";
import Station from "./station";

interface StationDescription {
  description: string;
  id: Station;
  name: string;
  relays: Relays;
  stream: string;
}

type Stations = StationDescription[];

export default Stations;
