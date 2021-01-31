import Station from "./station";
import RainwaveTime from "./time";

export default interface User {
  admin: boolean;
  tuned_in: boolean;
  perks: boolean;
  request_position: number;
  request_expires_at: RainwaveTime;
  rate_anything: boolean;
  requests_paused: boolean;
  avatar?: string | null;
  new_privmsg?: number;
  listen_key: string | null;
  name: string;
  sid: Station;
  lock: boolean;
  lock_in_effect: boolean;
  lock_sid: Station | null;
  voted_entry: number;
  listener_id: number;
}
