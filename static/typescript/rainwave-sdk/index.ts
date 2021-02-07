import { RainwaveSDKUsageError } from "./errors";
import RainwaveEventListener from "./eventListener";
import RainwaveRequest from "./request";
import { RainwaveRequests } from "./requestTypes";
import { ALL_RAINWAVE_RESPONSE_KEYS, RainwaveResponseTypes } from "./responseTypes";
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

const PING_INTERVAL = 20000;
const WEBSOCKET_CHECK_TIMEOUT_MS = 3000;
const DEFAULT_RECONNECT_TIMEOUT = 500;
const STATELESS_REQUESTS = ["ping", "pong"];
const MAX_QUEUED_REQUESTS = 10;
const SINGLE_REQUEST_TIMEOUT = 4000;

export default class Rainwave<
  K extends keyof RainwaveRequests
> extends RainwaveEventListener<RainwaveResponseTypes> {
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
  private _requestQueue: RainwaveRequest<K>[] = [];
  private _sentRequests: RainwaveRequest<K>[] = [];

  constructor(
    options: Partial<RainwaveOptions> &
      Pick<RainwaveOptions, "userId" | "apiKey" | "sid">
  ) {
    super(ALL_RAINWAVE_RESPONSE_KEYS);

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

  // Socket Functions **************************************************************************************

  private _socketSend(message: unknown): void {
    if (!this._socket) {
      throw new RainwaveSDKUsageError("Attempted to send to a disconnected socket.");
    }
    let jsonmsg: string;
    try {
      jsonmsg = JSON.stringify(message);
    } catch (error) {
      this.emit("sdk_exception", error);
      return;
    }
    try {
      this._socket.send(jsonmsg);
    } catch (error) {
      this.emit("sdk_exception", error);
    }
  }

  public startWebsocketSync(): void {
    if (this._socket?.readyState === WebSocket.OPEN) {
      return;
    }

    if (this._isOkTimer) {
      clearTimeout(this._isOkTimer);
    }
    this._isOkTimer = setTimeout(
      this._websocketCheck.bind(this),
      WEBSOCKET_CHECK_TIMEOUT_MS
    );

    const socket = new WebSocket(`${this._url}/websocket/${this._sid}`);
    socket.addEventListener("message", this._onMessage.bind(this));
    socket.addEventListener("close", this._onSocketClose.bind(this));
    socket.addEventListener("error", this._onSocketError.bind(this));
    socket.addEventListener("open", () => {
      this._debug("Socket open.");
      this._socketOpped = false;
      this._socketSend({
        action: "auth",
        user_id: this._userId,
        key: this._apiKey,
      });
    });
  }

  private _websocketCheck(): void {
    this._debug("Couldn't appear to connect.");
    this._forceReconnect();
  }

  private _cleanVariablesOnClose(): void {
    this._isOk = false;
    if (this._isOkTimer) {
      clearTimeout(this._isOkTimer);
      this._isOkTimer = null;
    }
    if (this._pingInterval) {
      clearInterval(this._pingInterval);
      this._pingInterval = null;
    }
  }

  public stopWebsocketSync(): void {
    if (
      !this._socket ||
      this._socket.readyState === WebSocket.CLOSING ||
      this._socket.readyState === WebSocket.CLOSED
    ) {
      return;
    }

    // sometimes depending on browser condition, onSocketClose won't get called for a while.
    // therefore it's important to clean here *and* in onSocketClose.
    this._cleanVariablesOnClose();
    this._socketStaysClosed = true;
    this._socket.close();
    this._debug("Socket closed.");
  }

  private _onSocketClose(event: Event): void {
    if (this._socketStaysClosed) {
      return;
    }

    this._debug("Socket was closed.");

    if (!this._socketOpped) {
      this._socketNoops += 1;
      if (this._maxRetries > 0 && this._socketNoops >= this._maxRetries) {
        this._onSocketError(event);
      }
    }

    setTimeout(this.startWebsocketSync.bind(this), DEFAULT_RECONNECT_TIMEOUT);
  }

  private _onSocketError(event: Event): void {
    this._debug(`Socket errored out, retrying.`);
    this.emit("error", { code: 0, tl_key: "sync_retrying", text: "" });
    this._userOnSocketError(event);
  }

  private _onSocketOK(): void {
    this._debug("wsok received - auth was good!");
    this.emit("sdk_error_clear", { tl_key: "sync_retrying" });
    this._isOk = true;

    if (!this._pingInterval) {
      this._pingInterval = setInterval(this._ping.bind(this), PING_INTERVAL);
    }

    if (this._currentScheduleId) {
      this._debug(
        `Socket send - check_sched_current_id with ${this._currentScheduleId}`
      );
      this._socketSend({
        action: "check_sched_current_id",
        sched_id: this._currentScheduleId,
      });
    }

    this._nextRequest();
  }

  private _onSocketFailure(error: RainwaveError): void {
    if (error.tl_key === "auth_failed") {
      this._debug(
        "Authorization failed for Rainwave websocket.  Wrong API key/user ID combo."
      );
      this.emit("error", error);
      this.stopWebsocketSync();
    }
  }

  // Error Handling ****************************************************************************************

  private _closeSocket(): void {
    if (this._socket) {
      this._socket.close();
    }
  }

  private _forceReconnect(): void {
    if (this._socketStaysClosed) {
      return;
    }
    this._debug("Forcing socket reconnect.");
    this._closeSocket();
  }

  // Ping and Pong *****************************************************************************************

  private _ping(): void {
    this._debug("Pinging server.");
    this._socketSend("ping");
  }

  private _onPing(): void {
    this._debug("Server ping.");
    this._socketSend("pong");
  }

  // Data From API *****************************************************************************************

  private _onMessage(message: { data: string }): void {
    this._socketOpped = true;
    this._socketNoops = 0;
    this.emit("sdk_error_clear", { tl_key: "sync_retrying" });
    if (this._isOkTimer) {
      clearTimeout(this._isOkTimer);
      this._isOkTimer = null;
    }

    let json: Partial<RainwaveResponseTypes>;
    try {
      json = JSON.parse(message.data) as Partial<RainwaveResponseTypes>;
    } catch (error) {
      this._debug(JSON.stringify(message));
      this._debug(error);
      this._closeSocket();
      return;
    }

    if (!json) {
      this._debug(JSON.stringify(message));
      this._debug("Response from Rainwave API was blank!");
      this._closeSocket();
    }

    const matchingSentRequest = this._sentRequests.find(
      (rq) => rq.messageId === json.message_id
    );

    if (matchingSentRequest) {
      this._sentRequests = this._sentRequests.filter(
        (rq) => rq.messageId !== json.message_id
      );
      if (json.error) {
        matchingSentRequest.reject(json.error);
      } else {
        matchingSentRequest.resolve(json);
      }
    }

    if (json.sync_result) {
      if (json.sync_result.tl_key === "station_offline") {
        this.emit("error", json.sync_result);
      } else {
        this.emit("sdk_error_clear", { tl_key: "station_offline" });
      }
    }

    this._performCallbacks(json);
    this._nextRequest();
  }

  // Calls To API ******************************************************************************************

  private _request(
    action: K,
    params: RainwaveRequests[K]["params"],
    resolve: (data: RainwaveRequests[K]["response"]) => void,
    reject: (error: RainwaveResponseTypes["error"]) => void
  ): void {
    if (!action) {
      throw "No action specified for Rainwave API request.";
    }
    const request = new RainwaveRequest<K>(action, params, resolve, reject);
    if (STATELESS_REQUESTS.indexOf(action) !== -1 || !this._isOk) {
      this._requestQueue = this._requestQueue.filter((rq) => rq.action !== action);
    }
    this._requestQueue.push(request);
    if (!this._socketIsBusy && this._isOk) {
      this._nextRequest();
    }
  }

  private _nextRequest(): void {
    const request = this._requestQueue.shift();

    if (!request) {
      this._socketIsBusy = false;
      return;
    }
    if (!this._isOk) {
      return;
    }

    if (STATELESS_REQUESTS.indexOf(request.action) === -1) {
      request.messageId = this._getNextRequestId();
      if (this._sentRequests.length > MAX_QUEUED_REQUESTS) {
        this._sentRequests.splice(0, this._sentRequests.length - MAX_QUEUED_REQUESTS);
      }
    }

    if (this._isOkTimer) {
      clearTimeout(this._isOkTimer);
    }
    this._isOkTimer = setTimeout(() => {
      this._onRequestTimeout(request);
    }, SINGLE_REQUEST_TIMEOUT);

    this._socketSend(request.apiMessage(this._sid));
    this._sentRequests.push(request);
  }

  private _onRequestTimeout(request: RainwaveRequest<K>): void {
    if (this._isOkTimer) {
      this._isOkTimer = null;
      this._requestQueue.unshift(request);
      this._debug("Looks like the connection timed out.");
      this.emit("error", { code: 0, text: "", tl_key: "sync_retrying" });
      this._forceReconnect();
    }
  }

  // Callback Handling *************************************************************************************

  private _performCallbacks(json: Partial<RainwaveResponseTypes>): void {
    // Make sure any vote results are registered after the schedule has been loaded.
    const alreadyVoted = json.already_voted;
    const liveVoting = json.live_voting;
    if (alreadyVoted) {
      delete json.already_voted;
    }
    if (liveVoting) {
      delete json.live_voting;
    }

    Object.keys(json).forEach((responseKey) => {
      const typedKey = responseKey as keyof RainwaveResponseTypes;
      this.emit(typedKey, json[typedKey]);
    });

    if ("sched_current" in json) {
      this.emit("sdk_schedule_synced", true);
    }

    if (alreadyVoted) {
      this.emit("already_voted", alreadyVoted);
    }

    if (liveVoting) {
      this.emit("live_voting", liveVoting);
    }
  }

  // API calls ***********************************************************************************************

  album(
    options: RainwaveRequests["album"]["params"]
  ): Promise<RainwaveRequests["album"]["response"]> {
    return new Promise((resolve, reject) => {
      this._request("album", options, resolve, reject);
    });
  }

  // public async allAlbums(): Promise<RainwaveResponseTypes["all_albums_by_cursor"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async allArtists(noSearchable = true): Promise<RainwaveResponseTypes["all_artists"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async allFaves(): Promise<RainwaveResponseTypes["all_faves"]> {
  //   // standard paged
  // }

  // public async allGroups(
  //   noSearchable = true,
  //   all = False
  // ): Promise<RainwaveResponseTypes["all_groups"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async allSongs(
  //   order: "rating" | undefined = undefined
  // ): Promise<RainwaveResponseTypes["all_songs"]> {
  //   // standard paged
  // }

  // public async artist(id: number): Promise<RainwaveResponseTypes["artist"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async clearRating(songId: number): Promise<RainwaveResponseTypes["rate_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async clearRequests(): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async clearRequestsOnCooldown(): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async deleteRequest(songId: number): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async faveAlbum(
  //   albumId: number,
  //   fave: boolean
  // ): Promise<RainwaveResponseTypes["fave_album_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async faveAllSongs(
  //   albumId: number,
  //   fave: boolean
  // ): Promise<RainwaveResponseTypes["fave_all_songs_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async faveSong(
  //   songId: number,
  //   fave: boolean
  // ): Promise<RainwaveResponseTypes["fave_song_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async group(id: number): Promise<RainwaveResponseTypes["group"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async infoAll(): Promise<RainwaveResponseTypes["all_stations_info"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async listener(id: number): Promise<RainwaveResponseTypes["listener"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async orderRequests(order: number[]): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async pauseRequestQueue(): Promise<
  //   RainwaveResponseTypes["pause_request_queue_result"]
  // > {
  //   return Promise.reject("unimplemented");
  // }

  // public async playbackHistory(): Promise<RainwaveResponseTypes["playback_history"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async rate(
  //   songId: number,
  //   rating: 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 4.5 | 5.0
  // ): Promise<RainwaveResponseTypes["rate_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async request(songId: number): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async requestFavoritedSongs(
  //   limit?: number
  // ): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async requestLine(): Promise<RainwaveResponseTypes["request_line_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async requestUnratedSongs(limit?: number): Promise<RainwaveResponseTypes["requests"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async search(search: string): Promise<RainwaveResponseTypes["search_results"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async song(id: number): Promise<RainwaveResponseTypes["song"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async stationSongCount(): Promise<RainwaveResponseTypes["station_song_count"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async stations(): Promise<RainwaveResponseTypes["stations"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async top100(): Promise<RainwaveResponseTypes["top_100"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async unpauseRequestQueue(): Promise<
  //   RainwaveResponseTypes["unpause_request_queue_result"]
  // > {
  //   return Promise.reject("unimplemented");
  // }

  // public async unratedSongs(): Promise<RainwaveResponseTypes["unrated_songs"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async userInfo(): Promise<RainwaveResponseTypes["user_info_result"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async userRecentVotes(): Promise<RainwaveResponseTypes["user_recent_votes"]> {
  //   return Promise.reject("unimplemented");
  // }

  // public async userRequestedHistory(): Promise<
  //   RainwaveResponseTypes["user_requested_history"]
  // > {
  //   return Promise.reject("unimplemented");
  // }

  // public async vote(entryId: number): Promise<RainwaveResponseTypes["vote_result"]> {
  //   return Promise.reject("unimplemented");
  // }
}
