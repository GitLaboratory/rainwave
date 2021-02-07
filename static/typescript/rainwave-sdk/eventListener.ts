type Listener<T> = (data: T) => void;

export default class RainwaveEventListener<E> {
  #listeners: { [K in keyof E]?: Listener<E[K]>[] } = {} as {
    [K in keyof E]?: Listener<E[K]>[];
  };

  constructor() {
    this.#listeners = {};
  }

  public on<K extends keyof E>(event: K, fn: Listener<E[K]>): void {
    const eListeners = this.#listeners[event];
    if (eListeners) {
      eListeners.push(fn);
    } else {
      this.#listeners[event] = [fn];
    }
  }

  public off<K extends keyof E>(event: K, fn: Listener<E[K]>): void {
    const eListeners = this.#listeners[event];
    if (eListeners) {
      this.#listeners[event] = eListeners.filter((listener) => listener !== fn);
    }
  }

  public emit<K extends keyof E>(event: K, data: E[K]): void {
    const eListeners = this.#listeners[event];
    if (eListeners) {
      eListeners.forEach((listener) => listener(data));
    }
  }

  public listeners<K extends keyof E>(event: K): Listener<E[K]>[] | undefined {
    return this.#listeners[event];
  }

  public listenersCount<K extends keyof E>(event: K): number {
    return this.#listeners[event]?.length ?? 0;
  }
}
