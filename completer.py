import readline

from pip._vendor.distlib.compat import raw_input


class Completer:
    def __init__(self, words):
        self.words = words
        self.prefix = None


    def complete(self, prefix, index):
        if prefix != self.prefix:
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
            ]
            self.prefix = prefix
            try:
                result = self.matching_words[index]
                index += 1
                return result
            except IndexError:
                return None


class askCompleter:
    def __init__(self, words):
        self.words = words
        self.prefix = None


    def setWords(self, words):
        self.words = words


    def ask(self, question, **kwargs):
        completer = Completer(self.words)


        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)

        if not 'null' in kwargs:
            null = False
        if null:
            return raw_input(question)
        else:
            ans = ''
        while not ans:
            ans = raw_input(question)
        return ans