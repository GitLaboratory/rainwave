interface Relay {
  name: string;
  protocol: "https://";
  hostname: string;
  port: 443;
}

type Relays = Relay[];

export default Relays;
