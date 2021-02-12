interface UserRecentVote {
  album_name: string;
  fave: boolean | null;
  id: number;
  rating: number | null;
  rating_user: number | null;
  title: string;
}

type UserRecentVotes = UserRecentVote[];

export default UserRecentVotes;
