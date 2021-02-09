interface LiveVotingEntry {
  entry_id: number;
  entry_votes: number;
  song_id: number;
}

type LiveVoting = Record<number, LiveVotingEntry[]>;

export default LiveVoting;
