class GroupBlocksElections:
    @property
    def songs_to_block(self):
        raise NotImplementedError

    def block_songs(self):
        pass

    class Meta:
        abstact = True
