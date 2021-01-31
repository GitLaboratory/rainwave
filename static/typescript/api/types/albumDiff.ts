import Album from "./album";

type AlbumDiff = Omit<Album, "rating_user">[];

export default AlbumDiff;
