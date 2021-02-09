import Station from "./station";

interface UpdatedAlbumRating {
  sid: Station;
  id: number;
  rating_user: number;
  rating_complete: boolean | null;
}

export default interface RateResult {
  updated_album_ratings: UpdatedAlbumRating[];
  song_id: number;
  rating_user: number;
  success: boolean;
  tl_key: string;
  text: string;
}
