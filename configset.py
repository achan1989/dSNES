def _add_comment(address, comment, store):
    assert address not in store
    store[address] = comment

def _get_comment(address, store):
    return store.get(address, None)


class Config():
    def __init__(self):
        self.forced_chunk_ends = []
        self.pre_comments = {}
        self.inline_comments = {}
        self.post_comments = {}

    def add_pre_comment(self, address, comment):
        return _add_comment(address, comment, self.pre_comments)

    def add_inline_comment(self, address, comment):
        return _add_comment(address, comment, self.inline_comments)

    def add_post_comment(self, address, comment):
        return _add_comment(address, comment, self.post_comments)

    def get_pre_comment(self, address):
        return _get_comment(address, self.pre_comments)

    def get_inline_comment(self, address):
        return _get_comment(address, self.inline_comments)

    def get_post_comment(self, address):
        return _get_comment(address, self.post_comments)


class NullConfig():
    def get_pre_comment(self, address):
        return None

    def get_inline_comment(self, address):
        return None

    def get_post_comment(self, address):
        return None
