type Listener<T> = (data: T) => void;

export default class RainwaveEventListener<E> {
  #listeners: { [K in keyof E]: Listener<E[K]>[] } = {} as {
    [K in keyof E]: Listener<E[K]>[];
  };

  constructor(keys: (keyof E)[]) {
    this.#listeners = keys.reduce(
      (acc, key) => ({ ...acc, [key]: [] }),
      {} as { [K in keyof E]: Listener<E[K]>[] }
    );
  }

  public on<K extends keyof E>(event: K, fn: Listener<E[K]>): void {
    this.#listeners[event].push(fn);
  }

  public off<K extends keyof E>(event: K, fn: Listener<E[K]>): void {
    const listeners = this.#listeners[event];
    this.#listeners[event] = listeners.filter((listener) => listener !== fn);
  }

  public emit<K extends keyof E>(event: K, data: E[K]): void {
    const listeners = this.#listeners[event];
    listeners.forEach((listener) => listener(data));
  }

  public listeners<K extends keyof E>(event: K): Listener<E[K]>[] {
    return this.#listeners[event];
  }

  public listenersCount<K extends keyof E>(event: K): number {
    return this.#listeners[event].length ?? 0;
  }
}
