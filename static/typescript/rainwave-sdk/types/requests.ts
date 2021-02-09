import ElecBlockedBy from "./elecBlockBy";
import Station from "./station";

interface RequestAlbum {
  name: string;
  id: number;
  rating: number;
  rating_user: number | null;
  rating_complete: boolean | null;
  art: string | null;
}

interface Request {
  id: number;
  sid: Station;
  origin_sid: Station;
  order: number;
  request_id: number;
  rating: number;
  title: string;
  length: number;
  cool: boolean;
  cool_end: number;
  good: boolean;
  elec_blocked: boolean;
  elec_blocked_by: ElecBlockedBy;
  elec_blocked_num: number | null;
  valid: boolean;
  rating_user: number;
  fave: boolean | null;
  albums: [RequestAlbum];
}

type Requests = Request[];

export default Requests;
