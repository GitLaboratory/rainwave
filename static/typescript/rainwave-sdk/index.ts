import { RainwaveSDKUsageError } from "./errors";
import RainwaveEventListener from "./eventListener";
import RainwaveRequest from "./request";
import { RainwaveRequests } from "./requestTypes";
import { RainwaveResponseTypes } from "./responseTypes";
import RainwaveError from "./types/error";
import Station from "./types/station";

interface RainwaveOptions {
  userId: number;
  apiKey: string;
  sid: Station;
  url: string;
  debug: (msg: string | Error) => void;
  maxRetries: number;
  onSocketError: (event: Event) => void;
}

export default class Rainwave extends RainwaveEventListener<RainwaveResponseTypes> {
  private _userId: number;
  private _apiKey: string;
  private _sid: Station;
  private _url: string;
  private _debug: (msg: string) => void;
  private _userOnSocketError: (event: Event) => void;
  private _socket?: WebSocket;
  private _isOk?: boolean = false;
  private _isOkTimer: number | null = null;
  private _pingInterval: number | null = null;
  private _socketOpped: boolean = false;
  private _socketStaysClosed: boolean = false;
  private _maxRetries: number;
  private _socketNoops: number = 0;
  private _socketIsBusy: boolean = false;

  private _currentScheduleId: number | undefined;
  private _requestId: number = 0;
  private _requestQueue: RainwaveRequest<keyof RainwaveRequests>[] = [];
  private _sentRequests: RainwaveRequest<keyof RainwaveRequests>[] = [];

  constructor(
    options: Partial<RainwaveOptions> &
      Pick<RainwaveOptions, "userId" | "apiKey" | "sid">
  ) {
    super();

    this._userId = options.userId;
    this._apiKey = options.apiKey;
    this._sid = options.sid;
    this._url = options.url || "wss://rainwave.cc/api4/websocket/";
    this._debug = options?.debug || ((): void => {});
    this._maxRetries = options?.maxRetries ?? 0;
    this._userOnSocketError = options?.onSocketError || ((): void => {});

    this.on("wsok", this._onSocketOK.bind(this));
    this.on("wserror", this._onSocketFailure.bind(this));
    this.on("ping", this._onPing.bind(this));
  }

  private _getNextRequestId(): number {
    this._requestId += 1;
    return this._requestId;
  }


  // API calls ***********************************************************************************************

  album(
    params: RainwaveRequests["album"]["params"]
  ): Promise<RainwaveRequests["album"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "album",
          params,
          (data) => resolve(data as RainwaveRequests["album"]["response"]),
          reject
        )
      );
    });
  }

  allAlbumsByCursor(): Promise<RainwaveRequests["all_albums_by_cursor"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "all_albums_by_cursor",
          { noSearchable: true },
          (data) =>
            resolve(data as RainwaveRequests["all_albums_by_cursor"]["response"]),
          reject
        )
      );
    });
  }

  allArtists(): Promise<RainwaveRequests["all_artists"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "all_artists",
          { noSearchable: true },
          (data) => resolve(data as RainwaveRequests["all_artists"]["response"]),
          reject
        )
      );
    });
  }

  allFaves(): Promise<RainwaveRequests["all_faves"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "all_faves",
          {},
          (data) => resolve(data as RainwaveRequests["all_faves"]["response"]),
          reject
        )
      );
    });
  }

  allGroups(): Promise<RainwaveRequests["all_groups"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "all_groups",
          { noSearchable: true },
          (data) => resolve(data as RainwaveRequests["all_groups"]["response"]),
          reject
        )
      );
    });
  }

  allSongs(
    params: RainwaveRequests["all_songs"]["params"]
  ): Promise<RainwaveRequests["all_songs"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "all_songs",
          params,
          (data) => resolve(data as RainwaveRequests["all_songs"]["response"]),
          reject
        )
      );
    });
  }

  artist(
    params: RainwaveRequests["artist"]["params"]
  ): Promise<RainwaveRequests["artist"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "artist",
          params,
          (data) => resolve(data as RainwaveRequests["artist"]["response"]),
          reject
        )
      );
    });
  }

  clearRating(
    params: RainwaveRequests["clear_rating"]["params"]
  ): Promise<RainwaveRequests["clear_rating"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "clear_rating",
          params,
          (data) => resolve(data as RainwaveRequests["clear_rating"]["response"]),
          reject
        )
      );
    });
  }

  clearRequests(): Promise<RainwaveRequests["clear_requests"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "clear_requests",
          {},
          (data) => resolve(data as RainwaveRequests["clear_requests"]["response"]),
          reject
        )
      );
    });
  }

  clearRequestsOnCooldown(): Promise<
    RainwaveRequests["clear_requests_on_cooldown"]["response"]
  > {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "clear_requests_on_cooldown",
          {},
          (data) =>
            resolve(data as RainwaveRequests["clear_requests_on_cooldown"]["response"]),
          reject
        )
      );
    });
  }

  deleteRequest(
    params: RainwaveRequests["delete_request"]["params"]
  ): Promise<RainwaveRequests["delete_request"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "delete_requests",
          params,
          (data) => resolve(data as RainwaveRequests["delete_request"]["response"]),
          reject
        )
      );
    });
  }

  faveAlbum(
    params: RainwaveRequests["fave_album"]["params"]
  ): Promise<RainwaveRequests["fave_album"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "fave_album",
          params,
          (data) => resolve(data as RainwaveRequests["fave_album"]["response"]),
          reject
        )
      );
    });
  }

  faveAllSongs(
    params: RainwaveRequests["fave_all_songs"]["params"]
  ): Promise<RainwaveRequests["fave_all_songs"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "fave_all_songs",
          params,
          (data) => resolve(data as RainwaveRequests["fave_all_songs"]["response"]),
          reject
        )
      );
    });
  }

  faveSong(
    params: RainwaveRequests["fave_song"]["params"]
  ): Promise<RainwaveRequests["fave_song"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "fave_song",
          params,
          (data) => resolve(data as RainwaveRequests["fave_song"]["response"]),
          reject
        )
      );
    });
  }

  group(
    params: RainwaveRequests["group"]["params"]
  ): Promise<RainwaveRequests["group"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "group",
          params,
          (data) => resolve(data as RainwaveRequests["group"]["response"]),
          reject
        )
      );
    });
  }

  infoAll(): Promise<RainwaveRequests["info_all"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "info_all",
          {},
          (data) => resolve(data as RainwaveRequests["info_all"]["response"]),
          reject
        )
      );
    });
  }

  listener(
    params: RainwaveRequests["listener"]["params"]
  ): Promise<RainwaveRequests["listener"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "listener",
          params,
          (data) => resolve(data as RainwaveRequests["listener"]["response"]),
          reject
        )
      );
    });
  }

  orderRequests(
    params: RainwaveRequests["order_requests"]["params"]
  ): Promise<RainwaveRequests["order_requests"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "order_requests",
          params,
          (data) => resolve(data as RainwaveRequests["order_requests"]["response"]),
          reject
        )
      );
    });
  }

  pauseRequestQueue(): Promise<RainwaveRequests["pause_request_queue"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "pause_request_queue",
          {},
          (data) =>
            resolve(data as RainwaveRequests["pause_request_queue"]["response"]),
          reject
        )
      );
    });
  }

  playbackHistory(): Promise<RainwaveRequests["playback_history"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "playback_history",
          {},
          (data) => resolve(data as RainwaveRequests["playback_history"]["response"]),
          reject
        )
      );
    });
  }

  rate(
    params: RainwaveRequests["rate"]["params"]
  ): Promise<RainwaveRequests["rate"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "rate",
          params,
          (data) => resolve(data as RainwaveRequests["rate"]["response"]),
          reject
        )
      );
    });
  }

  request(
    params: RainwaveRequests["request"]["params"]
  ): Promise<RainwaveRequests["request"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "request",
          params,
          (data) => resolve(data as RainwaveRequests["request"]["response"]),
          reject
        )
      );
    });
  }

  requestFavoritedSongs(
    params: RainwaveRequests["request_favorited_songs"]["params"]
  ): Promise<RainwaveRequests["request_favorited_songs"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "request_favorited_songs",
          params,
          (data) =>
            resolve(data as RainwaveRequests["request_favorited_songs"]["response"]),
          reject
        )
      );
    });
  }

  requestLine(): Promise<RainwaveRequests["request_line"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "request_line",
          {},
          (data) => resolve(data as RainwaveRequests["request_line"]["response"]),
          reject
        )
      );
    });
  }

  requestUnratedSongs(
    params: RainwaveRequests["request_unrated_songs"]["params"]
  ): Promise<RainwaveRequests["request_unrated_songs"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "request_unrated_songs",
          params,
          (data) =>
            resolve(data as RainwaveRequests["request_unrated_songs"]["response"]),
          reject
        )
      );
    });
  }

  search(
    params: RainwaveRequests["search"]["params"]
  ): Promise<RainwaveRequests["search"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "search",
          params,
          (data) => resolve(data as RainwaveRequests["search"]["response"]),
          reject
        )
      );
    });
  }

  song(
    params: RainwaveRequests["song"]["params"]
  ): Promise<RainwaveRequests["song"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "song",
          params,
          (data) => resolve(data as RainwaveRequests["song"]["response"]),
          reject
        )
      );
    });
  }

  stationSongCount(): Promise<RainwaveRequests["station_song_count"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "station_song_count",
          {},
          (data) => resolve(data as RainwaveRequests["station_song_count"]["response"]),
          reject
        )
      );
    });
  }

  stations(): Promise<RainwaveRequests["stations"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "stations",
          {},
          (data) => resolve(data as RainwaveRequests["stations"]["response"]),
          reject
        )
      );
    });
  }

  top100(): Promise<RainwaveRequests["top_100"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "top_100",
          {},
          (data) => resolve(data as RainwaveRequests["top_100"]["response"]),
          reject
        )
      );
    });
  }

  unpauseRequestQueue(): Promise<
    RainwaveRequests["unpause_request_queue"]["response"]
  > {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "unpause_request_queue",
          {},
          (data) =>
            resolve(data as RainwaveRequests["unpause_request_queue"]["response"]),
          reject
        )
      );
    });
  }

  unratedSongs(): Promise<RainwaveRequests["unrated_songs"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "unrated_songs",
          {},
          (data) => resolve(data as RainwaveRequests["unrated_songs"]["response"]),
          reject
        )
      );
    });
  }

  userInfo(): Promise<RainwaveRequests["user_info"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "user_info",
          {},
          (data) => resolve(data as RainwaveRequests["user_info"]["response"]),
          reject
        )
      );
    });
  }

  userRecentVotes(): Promise<RainwaveRequests["user_recent_votes"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "user_recent_votes",
          {},
          (data) => resolve(data as RainwaveRequests["user_recent_votes"]["response"]),
          reject
        )
      );
    });
  }

  userRequestedHistory(): Promise<
    RainwaveRequests["user_requested_history"]["response"]
  > {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "user_requested_history",
          {},
          (data) =>
            resolve(data as RainwaveRequests["user_requested_history"]["response"]),
          reject
        )
      );
    });
  }

  vote(
    params: RainwaveRequests["vote"]["params"]
  ): Promise<RainwaveRequests["vote"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request(
        new RainwaveRequest(
          "vote",
          params,
          (data) => resolve(data as RainwaveRequests["vote"]["response"]),
          reject
        )
      );
    });
  }
}
