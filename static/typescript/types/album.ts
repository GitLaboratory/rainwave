export interface Album {
  id: number;
  rating: number | null;
  art: string;
  name: string;
  rating_user: number | null;
  fave: boolean | null;
}

export default Album;
