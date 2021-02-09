import Station from "./station";
import RainwaveTime from "./time";

interface ListenerTopAlbum {
  id: number;
  name: string;
  rating_listener: number;
  rating: number;
}

interface ListenerTopRequestAlbum {
  id: number;
  name: string;
  request_count_listener: number;
}

interface ListenerVotesByStation {
  sid: Station;
  votes: number;
}

interface ListenerRequestsByStation {
  sid: Station;
  requests: number;
}

interface ListenerRatingsByStation {
  sid: Station;
  average_rating: string;
  ratings: number;
}

interface ListenerRatingSpreadItem {
  ratings: number;
  rating: number;
}

export default interface Listener {
  user_id: number;
  name: string;
  avatar: string | null;
  colour: string;
  rank: string;
  total_votes: number;
  total_ratings: number;
  mind_changes: number;
  total_requests: number;
  winning_votes: number;
  losing_votes: number;
  regdate: RainwaveTime;
  top_albums: ListenerTopAlbum[];
  top_request_albums: ListenerTopRequestAlbum[];
  votes_by_station: ListenerVotesByStation[];
  requests_by_station: ListenerRequestsByStation[];
  requests_by_source_station: ListenerRequestsByStation[];
  ratings_by_station: ListenerRatingsByStation[];
  ratings_completion: { [K in Exclude<Station, Station.all>]?: number };
  rating_spread: ListenerRatingSpreadItem[];
}
