import {
  ALL_RAINWAVE_RESPONSE_KEYS,
  RainwaveResponseKey,
  RainwaveResponseTypes,
} from "./responseTypes";
import Station from "./types/station";

type Listener = (data: RainwaveResponseTypes[RainwaveResponseKey]) => void;
type Listeners = Record<RainwaveResponseKey, Listener[]>;

interface RainwaveOptions {
  userId: number;
  apiKey: string;
  sid: Station;
  url: string;
  debug: (msg: string) => void;
  maxRetries: number;
  onSocketError: (error: Error) => void;
}

const WEBSOCKET_CHECK_TIMEOUT_MS = 3000;
const DEFAULT_RECONNECT_TIMEOUT = 500;

export default class Rainwave {
  #listeners: Listeners = ALL_RAINWAVE_RESPONSE_KEYS.reduce(
    (accumulated, key) => ({ ...accumulated, [key]: [] }),
    {} as Listeners
  );

  #userId: number;
  #apiKey: string;
  #sid: Station;
  #url: string;
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
    options: Partial<RainwaveOptions> &
      Pick<RainwaveOptions, "userId" | "apiKey" | "sid">
  ) {
    this.#userId = options.userId;
    this.#apiKey = options.apiKey;
    this.#sid = options.sid;
    this.#url = options.url || "wss://rainwave.cc/api4/websocket/";
    this.#debug = options?.debug || ((): void => {});
    this.#maxRetries = options?.maxRetries ?? 0;
    this.#onSocketError = options?.onSocketError || ((): void => {});
  }

  private _addListener(event: RainwaveResponseKey, fn: Listener): void {
    this.#listeners[event].push(fn);
  }

  public on(event: RainwaveResponseKey, fn: Listener): void {
    this._addListener(event, fn);
  }

  public off(event: RainwaveResponseKey, fn: Listener): void {
    const existingListeners = this.#listeners[event];
    const oopsiePookums = existingListeners.filter((listener) => listener !== fn);
    this.#listeners[event] = oopsiePookums;
  }

  public emit<K extends RainwaveResponseKey>(
    event: K,
    data: RainwaveResponseTypes[K]
  ): void {
    const listeners = this.#listeners[event];
    listeners.forEach((listener) => listener(data));
  }

  public listeners(event: RainwaveResponseKey): Listener[] {
    return this.#listeners[event];
  }

  public listenersCount<K extends RainwaveResponseKey>(event: K): number {
    return this.#listeners[event]?.length ?? 0;
  }

  // public async album(
  //   id: number,
  //   sort: "added_on" | undefined = undefined,
  //   allCategories?: boolean = true
  // ): Promise<RainwaveResponseTypes["album"]> {
  //   return Promise.reject("unimplemented");
  // }

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

  // public async info(): Promise<InfoRainwaveResponse> {
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

  // Socket Functions **************************************************************************************

  public startWebsocketSync(): void {
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

    const socket = new WebSocket(`${this.#url}/websocket/${this.#sid}`);
    socket.addEventListener("open", () => {
      this.#debug("Socket open.");
      this.#socketOpped = false;
      try {
        socket.send(
          JSON.stringify({
            action: "auth",
            user_id: this.#userId,
            key: this.#apiKey,
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
  // 		console.error("RainwaveResponse from Rainwave API was not JSON!");
  // 		console.error(message);
  // 		closeSocket();
  // 		if (asyncRequest) {
  // 			asyncRequest.onError();
  // 		}
  // 		return;
  // 	}

  // 	if (!json) {
  // 		console.error("RainwaveResponse from Rainwave API was blank!");
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

const test = new Rainwave({ userId: 1, apiKey: "1", sid: 1 });
test.on("album", (returnedAlbum) => {
  console.log(returnedAlbum);
});
