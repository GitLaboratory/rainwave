import { RainwaveSDKUsageError } from "./errors";
import { InfoResponse, ResponseTypes } from "./responseTypes";
import Station from "./types/station";

type Arguments<T> = [T] extends [(...args: infer U) => unknown]
  ? U
  : [T] extends [void]
  ? []
  : [T];

type Listener<T> = (...argv: Arguments<T>) => void;

type RainwaveEvents = {
  [K in keyof ResponseTypes]: (data: ResponseTypes[K]) => void;
};

class EventDescription<T extends () => void> {
  constructor(public readonly fn: T, public readonly once: boolean) {}
}

interface RainwaveRequestOptions {
  userId: number;
  apiKey: string;
  sid: Station;
  url: string;
}

interface RainwaveOptions {
  debug?: (msg: string) => void;
  maxRetries?: number;
  onSocketError?: (error: Error) => void;
}

const WEBSOCKET_CHECK_TIMEOUT_MS = 3000;
const DEFAULT_RECONNECT_TIMEOUT = 500;

export default class Rainwave<EVENTS = RainwaveEvents> {
  #listeners: {
    [K in keyof EVENTS]?: Array<EventDescription<Listener<EVENTS[K]>>>;
  } = {};

  #defaultRequestOptions: Partial<RainwaveRequestOptions>;
  #debug: (msg: string) => void;
  #onSocketError: (error: Error) => void;
  #socket?: WebSocket;
  #isOk?: boolean = false;
  #isOkTimer: number | null = null;
  #pingInterval: number | null = null;
  #socketOpped: boolean = false;
  #socketStaysClosed: boolean = false;
  #maxRetries: number;
  #socketNoops: number = 0;

  #currentScheduleId: number | undefined;
  #requestId: number = 0;
  #requestQueue: Record<string, unknown>[] = [];
  #sentRequests: Record<string, unknown>[] = [];

  constructor(
    defaultRequestOptions: Partial<RainwaveRequestOptions>,
    options?: RainwaveOptions
  ) {
    this.#defaultRequestOptions = {
      userId: defaultRequestOptions.userId,
      apiKey: defaultRequestOptions.apiKey,
      sid: defaultRequestOptions.sid,
      url: defaultRequestOptions.url || "wss://rainwave.cc/api4/websocket/",
    };

    this.#debug = options?.debug || ((): void => {});
    this.#maxRetries = options?.maxRetries ?? 0;
    this.#onSocketError = options?.onSocketError || ((): void => {});
  }

  private _getRequestOptions(
    requestOptions?: Partial<RainwaveRequestOptions>
  ): RainwaveRequestOptions {
    const apiKey = this.#defaultRequestOptions.apiKey || requestOptions?.apiKey;
    if (!apiKey) {
      throw new RainwaveSDKUsageError("Missing 'apiKey' option for Rainwave request.");
    }
    const sid = this.#defaultRequestOptions.sid || requestOptions?.sid;
    if (!sid) {
      throw new RainwaveSDKUsageError(
        "Missing 'sid' (station ID) option for Rainwave request."
      );
    }
    const userId = this.#defaultRequestOptions.userId || requestOptions?.userId;
    if (!userId) {
      throw new RainwaveSDKUsageError("Missing `userId` option for Rainwave request.");
    }
    const url = this.#defaultRequestOptions.url || requestOptions?.url;
    if (!url) {
      throw new RainwaveSDKUsageError("Missing `url` option for Rainwave.");
    }
    return {
      apiKey,
      sid,
      userId,
      url,
    };
  }

  private _addEvent<K extends keyof EVENTS>(
    event: K,
    fn: Listener<EVENTS[K]>,
    once: boolean
  ): this {
    if (!this.#listeners[event]) {
      this.#listeners[event] = [];
    }
    this.#listeners[event]?.push(new EventDescription(fn, once));
    return this;
  }

  public on<K extends keyof EVENTS>(event: K, fn: Listener<EVENTS[K]>): this {
    return this._addEvent(event, fn, false);
  }

  public once<K extends keyof EVENTS>(event: K, fn: Listener<EVENTS[K]>): this {
    return this._addEvent(event, fn, true);
  }

  public off<K extends keyof EVENTS>(event: K, fn: Listener<EVENTS[K]>): this {
    if (this.#listeners[event]) {
      const listeners = this.#listeners[event];
      if (listeners) {
        this.#listeners[event] = listeners.filter(
          (description) => description.fn !== fn
        );

        if (listeners.length === 0) {
          delete this.#listeners[event];
        }
      }
    }
    return this;
  }

  public removeAllListeners<K extends keyof EVENTS>(event?: K): this {
    if (event) {
      delete this.#listeners[event];
    } else {
      this.#listeners = {};
    }
    return this;
  }

  public emit<K extends keyof EVENTS>(event: K, ...argv: Arguments<EVENTS[K]>): this {
    const listeners = this.#listeners[event];
    if (listeners) {
      this.#listeners[event] = listeners.filter((description) => {
        description.fn.call(this, ...argv);
        return !description.once;
      });
    }
    return this;
  }

  public listeners<K extends keyof EVENTS>(event: K): Listener<EVENTS[K]>[] {
    return this.#listeners[event]?.map((description) => description.fn) || [];
  }

  public listenersCount<K extends keyof EVENTS>(event: K): number {
    return this.#listeners[event]?.length ?? 0;
  }

  public async album(
    id: number,
    sort: "added_on" | undefined = undefined,
    allCategories?: boolean = true
  ): Promise<ResponseTypes["album"]> {
    return Promise.reject("unimplemented");
  }

  public async allAlbums(): Promise<ResponseTypes["all_albums_by_cursor"]> {
    return Promise.reject("unimplemented");
  }

  public async allArtists(noSearchable = true): Promise<ResponseTypes["all_artists"]> {
    return Promise.reject("unimplemented");
  }

  public async allFaves(): Promise<ResponseTypes["all_faves"]> {
    // standard paged
  }

  public async allGroups(
    noSearchable = true,
    all = False
  ): Promise<ResponseTypes["all_groups"]> {
    return Promise.reject("unimplemented");
  }

  public async allSongs(
    order: "rating" | undefined = undefined
  ): Promise<ResponseTypes["all_songs"]> {
    // standard paged
  }

  public async artist(id: number): Promise<ResponseTypes["artist"]> {
    return Promise.reject("unimplemented");
  }

  public async clearRating(songId: number): Promise<ResponseTypes["rate_result"]> {
    return Promise.reject("unimplemented");
  }

  public async clearRequests(): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async clearRequestsOnCooldown(): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async deleteRequest(songId: number): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async faveAlbum(
    albumId: number,
    fave: boolean
  ): Promise<ResponseTypes["fave_album_result"]> {
    return Promise.reject("unimplemented");
  }

  public async faveAllSongs(
    albumId: number,
    fave: boolean
  ): Promise<ResponseTypes["fave_all_songs_result"]> {
    return Promise.reject("unimplemented");
  }

  public async faveSong(
    songId: number,
    fave: boolean
  ): Promise<ResponseTypes["fave_song_result"]> {
    return Promise.reject("unimplemented");
  }

  public async group(id: number): Promise<ResponseTypes["group"]> {
    return Promise.reject("unimplemented");
  }

  public async info(): Promise<InfoResponse> {
    return Promise.reject("unimplemented");
  }

  public async infoAll(): Promise<ResponseTypes["all_stations_info"]> {
    return Promise.reject("unimplemented");
  }

  public async listener(id: number): Promise<ResponseTypes["listener"]> {
    return Promise.reject("unimplemented");
  }

  public async orderRequests(order: number[]): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async pauseRequestQueue(): Promise<
    ResponseTypes["pause_request_queue_result"]
  > {
    return Promise.reject("unimplemented");
  }

  public async playbackHistory(): Promise<ResponseTypes["playback_history"]> {
    return Promise.reject("unimplemented");
  }

  public async rate(
    songId: number,
    rating: 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 4.5 | 5.0
  ): Promise<ResponseTypes["rate_result"]> {
    return Promise.reject("unimplemented");
  }

  public async request(songId: number): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async requestFavoritedSongs(
    limit?: number
  ): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async requestLine(): Promise<ResponseTypes["request_line_result"]> {
    return Promise.reject("unimplemented");
  }

  public async requestUnratedSongs(limit?: number): Promise<ResponseTypes["requests"]> {
    return Promise.reject("unimplemented");
  }

  public async search(search: string): Promise<ResponseTypes["search_results"]> {
    return Promise.reject("unimplemented");
  }

  public async song(id: number): Promise<ResponseTypes["song"]> {
    return Promise.reject("unimplemented");
  }

  public async stationSongCount(): Promise<ResponseTypes["station_song_count"]> {
    return Promise.reject("unimplemented");
  }

  public async stations(): Promise<ResponseTypes["stations"]> {
    return Promise.reject("unimplemented");
  }

  public async top100(): Promise<ResponseTypes["top_100"]> {
    return Promise.reject("unimplemented");
  }

  public async unpauseRequestQueue(): Promise<
    ResponseTypes["unpause_request_queue_result"]
  > {
    return Promise.reject("unimplemented");
  }

  public async unratedSongs(): Promise<ResponseTypes["unrated_songs"]> {
    return Promise.reject("unimplemented");
  }

  public async userInfo(): Promise<ResponseTypes["user_info_result"]> {
    return Promise.reject("unimplemented");
  }

  public async userRecentVotes(): Promise<ResponseTypes["user_recent_votes"]> {
    return Promise.reject("unimplemented");
  }

  public async userRequestedHistory(): Promise<
    ResponseTypes["user_requested_history"]
  > {
    return Promise.reject("unimplemented");
  }

  public async vote(entryId: number): Promise<ResponseTypes["vote_result"]> {
    return Promise.reject("unimplemented");
  }

  // Socket Functions **************************************************************************************

  public startWebsocketSync(requestOptions: RainwaveRequestOptions): void {
    if (this.#socket?.readyState === WebSocket.OPEN) {
      return;
    }

    if (this.#isOkTimer) {
      clearTimeout(this.#isOkTimer);
    }
    this.#isOkTimer = setTimeout(
      this._websocketCheck.bind(this),
      WEBSOCKET_CHECK_TIMEOUT_MS
    );

    const options = this._getRequestOptions(requestOptions);
    const socket = new WebSocket(`${options.url}/websocket/${options.sid}`);
    socket.addEventListener("open", () => {
      this.#debug("Socket open.");
      this.#socketOpped = false;
      try {
        socket.send(
          JSON.stringify({
            action: "auth",
            user_id: options.userId,
            key: options.apiKey,
          })
        );
      } catch (error) {
        this._onSocketError();
      }
    });
    socket.addEventListener("message", this._onMessage.bind(this));
    socket.addEventListener("close", this._onSocketClose.bind(this));
    socket.addEventListener("error", this._onSocketError.bind(this));
  }

  private _websocketCheck(): void {
    this.#debug("Couldn't appear to connect.");
    this._forceReconnect();
  }

  private _cleanVariablesOnClose(): void {
    this.#isOk = false;
    if (this.#isOkTimer) {
      clearTimeout(this.#isOkTimer);
      this.#isOkTimer = null;
    }
    if (this.#pingInterval) {
      clearInterval(this.#pingInterval);
      this.#pingInterval = null;
    }
  }

  public stopWebsocketSync(): void {
    if (
      !this.#socket ||
      this.#socket.readyState === WebSocket.CLOSING ||
      this.#socket.readyState === WebSocket.CLOSED
    ) {
      return;
    }

    // sometimes depending on browser condition, onSocketClose won't get called for a while.
    // therefore it's important to clean here to false here *and* on onSocketClose.
    this._cleanVariablesOnClose();
    this.#socketStaysClosed = true;
    this.#socket.close();
    this.#debug("Socket closed.");
  }

  private _onSocketClose(): void {
    this._onSocketClose();

    if (this.#socketStaysClosed) {
      return;
    }

    this.#debug("Socket was closed.");

    if (!this.#socketOpped) {
      this.#socketNoops += 1;
      if (this.#maxRetries > 0 && this.#socketNoops >= this.#maxRetries) {
        this._onSocketError();
      }
    }

    setTimeout(this.startWebsocketSync.bind(this), DEFAULT_RECONNECT_TIMEOUT);
  }

  private _onSocketError(): void {
    this.#debug(`Socket errored out, retrying.`);
    this.emit("error", { tl_key: "sync_retrying" });
  }

  // var onSocketOK = function() {
  // 	if (self.debug) console.log("wsok received - auth was good!");
  // 	self.onErrorRemove("sync_retrying");
  // 	this.#isOk = true;
  // 	isOK = true;

  // 	if (!pingInterval) {
  // 		pingInterval = setInterval(ping, 20000);
  // 	}

  // 	if (currentScheduleID) {
  // 		if (self.debug) console.log("Socket send - check_sched_current_id with " + currentScheduleID);
  // 		try {
  // 			socket.send(
  // 				JSON.stringify({
  // 					action: "check_sched_current_id",
  // 					sched_id: currentScheduleID
  // 				})
  // 			);
  // 		} catch (exc) {
  // 			console.error("Socket exception while trying to check_sched_current_id.");
  // 			console.error(exc);
  // 			onSocketError();
  // 		}
  // 	}

  // 	nextRequest();
  // };

  // var onSocketFailure = function(error) {
  // 	if (error.tl_key === "auth_failed") {
  // 		console.error("Authorization failed for Rainwave websocket.  Wrong API key/user ID combo.");
  // 		self.onError(error);
  // 		self.closePermanently();
  // 	}
  // };

  // // Error Handling ****************************************************************************************

  // self.onError = noop;
  // self.onErrorRemove = noop;
  // self.onUnsuccessful = noop;

  // self.forceReconnect = function() {
  // 	if (self.debug) console.log("Forcing socket reconnect.");
  // 	if (socketStaysClosed) {
  // 		return;
  // 	}
  // 	closeSocket();
  // };

  // self.closePermanently = function() {
  // 	if (self.debug) console.log("Forcing socket to be closed.");
  // 	socketStaysClosed = true;
  // 	closeSocket();
  // };

  // Visibility Changing ***********************************************************************************

  private _onVisibilityChange(): void {
    if (document.hidden) {
      this._closeWebsocket();
    } else {
      this._initWebSocket();
    }
  }

  // // Ping and Pong *****************************************************************************************

  // var ping = function() {
  // 	if (self.debug) console.log("Pinging server.");
  // 	self.request("ping");
  // };

  // var onPing = function() {
  // 	if (self.debug) console.log("Server ping.");
  // 	self.request("pong");
  // };

  // // Data From API *****************************************************************************************

  // var solveLatency = function(asyncRequest, latencies, threshold) {
  // 	var i,
  // 		avg = 0;
  // 	if (measuredRequests.indexOf(asyncRequest.action) !== -1) {
  // 		latencies.push(new Date() - asyncRequest.start);
  // 		while (latencies.length > 10) {
  // 			latencies.shift();
  // 		}
  // 		for (i = 0; i < latencies.length; i++) {
  // 			avg += latencies[i];
  // 		}
  // 		avg = avg / latencies.length;
  // 		self.slow = avg > threshold;
  // 	}
  // };

  // var onMessage = function(message) {
  // 	socketOpped = true;
  // 	socketNoops = 0;
  // 	self.onErrorRemove("sync_retrying");
  // 	if (isOkTimer) {
  // 		clearTimeout(isOkTimer);
  // 		isOkTimer = null;
  // 	}

  // 	var json;
  // 	try {
  // 		json = JSON.parse(message.data);
  // 	} catch (exc) {
  // 		console.error("Response from Rainwave API was not JSON!");
  // 		console.error(message);
  // 		closeSocket();
  // 		if (asyncRequest) {
  // 			asyncRequest.onError();
  // 		}
  // 		return;
  // 	}

  // 	if (!json) {
  // 		console.error("Response from Rainwave API was blank!");
  // 		console.error(message);
  // 		closeSocket();
  // 		if (asyncRequest) {
  // 			asyncRequest.onError();
  // 		}
  // 	}

  // 	if (self.debug) console.log("Socket receive", message.data);

  // 	var asyncRequest, i;
  // 	if (json.message_id) {
  // 		for (i = 0; i < sentRequests.length; i++) {
  // 			if (sentRequests[i].message.message_id === json.message_id.message_id) {
  // 				asyncRequest = sentRequests.splice(i, 1)[0];
  // 				asyncRequest.success = true;
  // 				solveLatency(asyncRequest, netLatencies, slowNetThreshold);
  // 				break;
  // 			}
  // 		}
  // 	}

  // 	if (asyncRequest) {
  // 		for (i in json) {
  // 			if ("success" in json[i] && !json[i].success) {
  // 				asyncRequest.success = false;
  // 				if (self.throwErrorsOnThrottle || json[i].tl_key !== "websocket_throttle") {
  // 					if (!asyncRequest.onError(json[i])) {
  // 						self.onUnsuccessful(json[i]);
  // 					}
  // 				}
  // 			}
  // 		}
  // 		asyncRequest.drawStart = new Date();
  // 	}

  // 	if ("sync_result" in json) {
  // 		if (json.sync_result.tl_key == "station_offline") {
  // 			self.onError(json.sync_result);
  // 		} else {
  // 			self.onErrorRemove("station_offline");
  // 		}
  // 	}

  // 	performCallbacks(json);

  // 	if (asyncRequest && asyncRequest.success) {
  // 		asyncRequest.onSuccess(json);
  // 		solveLatency(asyncRequest, drawLatencies, slowDrawThreshold);
  // 	}

  // 	nextRequest();
  // };

  // // Calls To API ******************************************************************************************

  // var statelessRequests = ["ping", "pong"];

  // self.onRequestError = null;

  // self.request = function(action, params, onSuccess, onError) {
  // 	if (!action) {
  // 		throw "No action specified for Rainwave API request.";
  // 	}
  // 	params = params || {};
  // 	params.action = action;
  // 	if ("sid" in params && !params.sid && params.sid !== 0) {
  // 		delete params.sid;
  // 	}
  // 	if (statelessRequests.indexOf(action) !== -1 || !isOK) {
  // 		for (var i = requestQueue.length - 1; i >= 0; i--) {
  // 			if (requestQueue[i].message.action === action) {
  // 				if (self.debug) console.log("Throwing away extra " + requestQueue[i].message.action);
  // 				requestQueue.splice(i, 1);
  // 			}
  // 		}
  // 	}
  // 	requestQueue.push({
  // 		message: params || {},
  // 		onSuccess: onSuccess || noop,
  // 		onError: onError || self.onRequestError || noop
  // 	});
  // 	if (!socketIsBusy && isOK) {
  // 		nextRequest();
  // 	}
  // };

  // var nextRequest = function() {
  // 	if (!requestQueue.length) {
  // 		socketIsBusy = false;
  // 		return;
  // 	}
  // 	if (!isOK) {
  // 		return;
  // 	}

  // 	var request = requestQueue[0];
  // 	request.start = new Date();

  // 	if (statelessRequests.indexOf(request.message.action) === -1) {
  // 		request.message.message_id = requestID;
  // 		requestID++;
  // 		if (sentRequests.length > 10) {
  // 			sentRequests.splice(0, sentRequests.length - 10);
  // 		}
  // 	}

  // 	if (isOkTimer) {
  // 		clearTimeout(isOkTimer);
  // 	}
  // 	isOkTimer = setTimeout(function() {
  // 		onRequestTimeout(request);
  // 	}, 4000);

  // 	if (self.debug) console.log("Socket write", request.message);

  // 	var jsonmsg;
  // 	try {
  // 		jsonmsg = JSON.stringify(request.message);
  // 	} catch (e) {
  // 		console.error("JSON exception while trying to encode message.");
  // 		console.error(e);
  // 		requestQueue.shift();
  // 		return;
  // 	}

  // 	try {
  // 		socket.send(jsonmsg);
  // 		requestQueue.shift();
  // 		if (request.message.message_id !== undefined) {
  // 			sentRequests.push(request);
  // 		}
  // 	} catch (exc) {
  // 		console.error("Socket exception while trying to send.");
  // 		console.error(exc);
  // 		onSocketError();
  // 	}
  // };

  // var onRequestTimeout = function(request) {
  // 	if (isOkTimer) {
  // 		isOkTimer = null;
  // 		requestQueue.unshift(request);
  // 		if (self.debug) console.log("Looks like the connection timed out.");
  // 		self.onRequestError({ tl_key: "lost_connection" });
  // 		self.onError({ tl_key: "sync_retrying" });
  // 		self.forceReconnect();
  // 	}
  // };

  // // Callback Handling *************************************************************************************

  // var performCallbacks = function(json) {
  // 	try {
  // 		// Make sure any vote results are registered after the schedule has been loaded.
  // 		var alreadyVoted;
  // 		var liveVoting;
  // 		if ("already_voted" in json) {
  // 			alreadyVoted = json.already_voted;
  // 			delete json.already_voted;
  // 		}
  // 		if ("live_voting" in json) {
  // 			liveVoting = json.live_voting;
  // 			delete json.live_voting;
  // 		}

  // 		var cb, key;
  // 		for (key in json) {
  // 			if (key in callbacks) {
  // 				for (cb = 0; cb < callbacks[key].length; cb++) {
  // 					callbacks[key][cb](json[key]);
  // 				}
  // 			}
  // 		}

  // 		if ("sched_current" in json) {
  // 			if (self.debug) console.log("Sync complete.");
  // 			performCallbacks({ _SYNC_SCHEDULE_COMPLETE: true });
  // 		}

  // 		key = "already_voted";
  // 		if (alreadyVoted && key in callbacks) {
  // 			for (cb = 0; cb < callbacks[key].length; cb++) {
  // 				callbacks[key][cb](alreadyVoted);
  // 			}
  // 		}

  // 		key = "live_voting";
  // 		if (liveVoting && key in callbacks) {
  // 			for (cb = 0; cb < callbacks[key].length; cb++) {
  // 				callbacks[key][cb](liveVoting);
  // 			}
  // 		}
  // 	} catch (e) {
  // 		if (self.exceptionHandler) {
  // 			self.exceptionHandler(e);
  // 		}
  // 		throw e;
  // 	}
}
