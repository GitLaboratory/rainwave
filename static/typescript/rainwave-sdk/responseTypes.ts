import Album from "./types/album";
import User from "./types/user";

export interface RainwaveResponseTypes {
  album: Album;
  all_albums_by_cursor: unknown;
  all_artists: unknown;
  all_faves: unknown;
  all_groups: unknown;
  all_songs: unknown;
  all_stations_info: unknown;
  already_voted: unknown;
  artist: unknown;
  build_version: unknown;
  cookie_domain: unknown;
  delete_request_result: unknown;
  error_report_result: unknown;
  error: unknown;
  fave_album_result: unknown;
  fave_all_songs_result: unknown;
  fave_song_result: unknown;
  group: unknown;
  listener: unknown;
  live_voting: unknown;
  locale: unknown;
  locales: unknown;
  mobile: unknown;
  on_draw: unknown;
  on_init: unknown;
  on_measure: unknown;
  pause_request_queue_result: unknown;
  playback_history: unknown;
  rate_result: unknown;
  redownload_m3u: unknown;
  relays: unknown;
  request_favorited_songs_result: unknown;
  request_line_result: unknown;
  request_line: unknown;
  request_result: unknown;
  request_unrated_songs_result: unknown;
  requests: unknown;
  sched_current: unknown;
  sched_history: unknown;
  sched_next: unknown;
  search_results: unknown;
  song: unknown;
  station_list: unknown;
  station_song_count: unknown;
  stations: unknown;
  stream_filename: unknown;
  top_100: unknown;
  unpause_request_queue_result: unknown;
  unrated_songs: unknown;
  user_info_result: unknown;
  user_recent_votes: unknown;
  user_requested_history: unknown;
  user: User;
  vote_result: unknown;
  websocket_host: unknown;
}

export const ALL_RAINWAVE_RESPONSE_KEYS: Array<keyof RainwaveResponseTypes> = [
  "album",
  "all_albums_by_cursor",
  "all_artists",
  "all_faves",
  "all_groups",
  "all_songs",
  "all_stations_info",
  "already_voted",
  "artist",
  "build_version",
  "cookie_domain",
  "delete_request_result",
  "error_report_result",
  "error",
  "fave_album_result",
  "fave_all_songs_result",
  "fave_song_result",
  "group",
  "listener",
  "live_voting",
  "locale",
  "locales",
  "mobile",
  "on_draw",
  "on_init",
  "on_measure",
  "pause_request_queue_result",
  "playback_history",
  "rate_result",
  "redownload_m3u",
  "relays",
  "request_favorited_songs_result",
  "request_line_result",
  "request_line",
  "request_result",
  "request_unrated_songs_result",
  "requests",
  "sched_current",
  "sched_history",
  "sched_next",
  "search_results",
  "song",
  "station_list",
  "station_song_count",
  "stations",
  "stream_filename",
  "top_100",
  "unpause_request_queue_result",
  "unrated_songs",
  "user_info_result",
  "user_recent_votes",
  "user_requested_history",
  "user",
  "vote_result",
  "websocket_host",
];

export type RainwaveResponseKey = typeof ALL_RAINWAVE_RESPONSE_KEYS[number];
