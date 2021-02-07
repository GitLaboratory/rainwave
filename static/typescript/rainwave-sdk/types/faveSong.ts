export default interface FaveSong {
  album_id: number;
  album_name: string;
  fave: boolean | null;
  id: number;
  rating: number;
  rating_user: number;
  title: string;
}
