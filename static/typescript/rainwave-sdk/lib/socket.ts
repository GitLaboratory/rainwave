import Ping from "../types/ping";
import Pong from "../types/pong";
import PongConfirm from "../types/pongConfirm";
import RainwaveError from "../types/error";
import RainwaveSDKErrorClear from "../types/errorClear";
import RainwaveEventListener from "../eventListener";

import RainwaveRequest from "../request";
import { RainwaveRequests } from "../requestTypes";
import { RainwaveResponseTypes } from "../responseTypes";
import { RainwaveSDKUsageError } from "../errors";

interface RainwaveWebSocketOptions {
  url?: string;
  debug?: (msg: string | Error) => void;
  maxRetries?: number;
  onSocketError?: (event: Event) => void;
}

type WebSocketState =
  | WebSocket.CONNECTING
  | WebSocket.OPEN
  | WebSocket.CLOSING
  | WebSocket.CLOSED;

const PING_INTERVAL = 20000;
const WEBSOCKET_CHECK_TIMEOUT_MS = 3000;
const DEFAULT_RECONNECT_TIMEOUT = 500;
const STATELESS_REQUESTS = ["ping", "pong"];
const MAX_QUEUED_REQUESTS = 10;
const SINGLE_REQUEST_TIMEOUT = 4000;

const RAINWAVE_URL = "wss://rainwave.cc/api4/websocket/";
const RAINWAVE_WEB_SOCKET_MAX_RETRIES = 0;

const RAINWAVE_WEB_SOCKET_EVENT_AUTH_OK = "wsok";
const RAINWAVE_WEB_SOCKET_EVENT_AUTH_ERROR = "wserror";
const RAINWAVE_WEB_SOCKET_EVENT_PING = "ping";

function RainwaveWebSocketDebug(): void {}
function RainwaveWebSocketOnError(): void {}

class RainwaveWebSocket extends RainwaveEventListener<RainwaveResponseTypes> {
  /**
   * Private Variables
   */
  #url: string;
  #debug: (message: string) => void;
  #maxRetries: number;
  #onSocketError: (event: Event) => void;
  #socket?: WebSocket;
  #isOperating: boolean = false;
  #nOperations: number = 0;

  #requestId: number = 0;
  #requestQueue: RainwaveRequest<keyof RainwaveRequests>[] = [];
  #sentRequests: RainwaveRequest<keyof RainwaveRequests>[] = [];

  #isOk?: boolean = false;
  #isOkTimer: number | null = null;

  #pingInterval: number | null = null;
  #socketStaysClosed: boolean = false;
  #socketNoops: number = 0;
  #socketIsBusy: boolean = false;

  /**
   * Constructor for initializing the web socket object.
   */
  constructor(options?: RainwaveWebSocketOptions) {
    super();

    this.#url = options?.url ?? RAINWAVE_URL;
    this.#debug = options?.debug ?? RainwaveWebSocketDebug;
    this.#maxRetries = options?.maxRetries ?? RAINWAVE_WEB_SOCKET_MAX_RETRIES;
    this.#onSocketError = options?.onSocketError ?? RainwaveWebSocketOnError;

    this.on("wsok", this._onSocketOK.bind(this));
    this.on("wserror", this._onSocketFailure.bind(this));
    this.on("ping", this._onPing.bind(this));
  }

  // Socket Functions **************************************************************************************

  private _getSocketState(): WebSocketState {
    return this.#socket?.readyState;
  }

  public start(): void {
    if (this._getSocketState() === WebSocket.OPEN) {
      return;
    }

    // if (this._isOkTimer) {
    //   clearTimeout(this._isOkTimer);
    // }

    // this._isOkTimer = setTimeout(
    //   this._websocketCheck.bind(this),
    //   WEBSOCKET_CHECK_TIMEOUT_MS
    // );

    const socket = new WebSocket(this.#url);

    socket.addEventListener("message", this._onMessage.bind(this));
    socket.addEventListener("close", this._onSocketClose.bind(this));
    socket.addEventListener("error", this._onSocketError.bind(this));

    socket.addEventListener("open", () => {
      this.#debug("Socket open.");
      this.#isOperating = false;
      this._socketSend({
        action: "auth",
        user_id: this._userId,
        key: this._apiKey,
      });
    });
  }

  private _parseMessage(message: string | Partial<RainwaveRequests>): string {
    if (typeof message === "string") {
      return message;
    }

    return JSON.stringify(message);
  }

  private _socketSend(message: string | Partial<RainwaveRequests>): void {
    if (!this.#socket) {
      throw new RainwaveSDKUsageError(
        "Attempted to send to a disconnected socket."
      );
      return;
    }

    try {
      const jsonMsg = this._parseMessage(message);
      this.#socket.send(jsonMsg);
    } catch (error) {
      this.emit("sdk_exception", error);
    }
  }

  private _websocketCheck(): void {
    this.#debug("Couldn't appear to connect.");
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
      !this.#socket ||
      this.#socket.readyState === WebSocket.CLOSING ||
      this.#socket.readyState === WebSocket.CLOSED
    ) {
      return;
    }

    // sometimes depending on browser condition, onSocketClose won't get called for a while.
    // therefore it's important to clean here *and* in onSocketClose.
    this._cleanVariablesOnClose();
    this.#socketStaysClosed = true;
    this.#socket.close();
    this.#debug("Socket closed.");
  }

  private _onSocketClose(event: Event): void {
    if (this.#socketStaysClosed) {
      return;
    }

    this.#debug("Socket was closed.");

    if (!this.#isOperating) {
      this.#nOperations += 1;
      if (this._maxRetries > 0 && this.#nOperations >= this._maxRetries) {
        this._onSocketError(event);
      }
    }

    setTimeout(this.startWebsocketSync.bind(this), DEFAULT_RECONNECT_TIMEOUT);
  }

  private _onSocketError(event: Event): void {
    this.#debug(`Socket errored out, retrying.`);
    this.emit("error", { code: 0, tl_key: "sync_retrying", text: "" });
    this._userOnSocketError(event);
  }

  private _onSocketOK(): void {
    this.#debug("wsok received - auth was good!");
    this.emit("sdk_error_clear", { tl_key: "sync_retrying" });
    this._isOk = true;

    if (!this._pingInterval) {
      this._pingInterval = setInterval(this._ping.bind(this), PING_INTERVAL);
    }

    if (this._currentScheduleId) {
      this.#debug(
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
      this.#debug(
        "Authorization failed for Rainwave websocket.  Wrong API key/user ID combo."
      );
      this.emit("error", error);
      this.stopWebsocketSync();
    }
  }

  // Error Handling ****************************************************************************************

  private _closeSocket(): void {
    if (this.#socket) {
      this.#socket.close();
    }
  }

  private _forceReconnect(): void {
    if (this.#socketStaysClosed) {
      return;
    }
    this.#debug("Forcing socket reconnect.");
    this._closeSocket();
  }

  // Ping and Pong *****************************************************************************************

  private _ping(): void {
    this.#debug("Pinging server.");
    this._socketSend("ping");
  }

  private _onPing(): void {
    this.#debug("Server ping.");
    this._socketSend("pong");
  }

  // Data From API *****************************************************************************************

  private _parseJson(data: string): Partial<RainwaveResponseTypes> | undefined {
    try {
      return JSON.parse(data) as Partial<RainwaveResponseTypes>;
    } catch (error) {
      this.#debug(JSON.stringify(data));
      this.#debug(error);
      this._closeSocket();
      return;
    }
  }

  private _onMessage(message: { data: string }): void {
    this.#isOperating = true;
    this.#nOperations = 0;

    this.emit("sdk_error_clear", { tl_key: "sync_retrying" });

    // if (this._isOkTimer) {
    //   clearTimeout(this._isOkTimer);
    //   this._isOkTimer = null;
    // }

    const json = this._parseJson(message.data);

    if (json === undefined) {
      this.#debug(JSON.stringify(message));
      this.#debug("Response from Rainwave API was blank!");
      this._closeSocket();
      return;
    }

    const matchingSentRequest = this.#sentRequests.find(
      (rq) => rq.messageId === json.message_id
    );

    if (matchingSentRequest) {
      this.#sentRequests = this.#sentRequests.filter(
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

  private _getNextRequestId(): number {
    this.#requestId += 1;
    return this.#requestId;
  }

  private _request(request: RainwaveRequest<keyof RainwaveRequests>): void {
    // if (STATELESS_REQUESTS.indexOf(request.action) !== -1 || !this._isOk) {

    if (STATELESS_REQUESTS.indexOf(request.action) !== -1) {
      this.#requestQueue = this.#requestQueue.filter(
        (rq) => rq.action !== request.action
      );
    }

    this.#requestQueue.push(request);

    // if (!this.#socketIsBusy && this._isOk) {
    if (!this.#socketIsBusy) {
      this._nextRequest();
    }
  }

  private _nextRequest(): void {
    const request = this.#requestQueue.shift();

    if (!request) {
      this.#socketIsBusy = false;
      return;
    }

    // if (!this._isOk) {
    //   return;
    // }

    if (STATELESS_REQUESTS.indexOf(request.action) === -1) {
      request.messageId = this._getNextRequestId();
      if (this.#sentRequests.length > MAX_QUEUED_REQUESTS) {
        this.#sentRequests.splice(
          0,
          this.#sentRequests.length - MAX_QUEUED_REQUESTS
        );
      }
    }

    // if (this._isOkTimer) {
    //   clearTimeout(this._isOkTimer);
    // }
    // this._isOkTimer = setTimeout(() => {
    //   this._onRequestTimeout(request);
    // }, SINGLE_REQUEST_TIMEOUT);

    this._socketSend(request.apiMessage(this.#sid));
    this.#sentRequests.push(request);
  }

  private _onRequestTimeout(
    request: RainwaveRequest<keyof RainwaveRequests>
  ): void {
    // if (this._isOkTimer) {
    //   this._isOkTimer = null;
    //   this.#requestQueue.unshift(request);
    //   this.#debug("Looks like the connection timed out.");
    //   this.emit("error", { code: 0, text: "", tl_key: "sync_retrying" });
    //   this._forceReconnect();
    // }
  }

  // Callback Handling *************************************************************************************

  private _performCallbacks(json: Partial<RainwaveResponseTypes>): void {
    // Make sure any vote results are registered after the schedule has been loaded.
    const votingKeys: (keyof RainwaveResponseTypes)[] = [
      "already_voted",
      "live_voting",
      "sched_current",
    ];

    const alreadyVoted = json.already_voted;
    const liveVoting = json.live_voting;

    Object.keys(json).forEach((responseKey) => {
      const typedKey = responseKey as keyof RainwaveResponseTypes;

      if (votingKeys.indexOf(typedKey) !== -1) {
        return;
      }

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
}

export { RainwaveWebSocket };
