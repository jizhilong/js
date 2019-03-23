class ChallengeDef:
    def is_triggered(self, record):
        """
        will the specified record trigger a progress updating on this challenge.
        """
        raise NotImplementedError

    def initial(self):
        """"
        create initial challenge progress
        """
        raise NotImplementedError

    def on_update(self, progress, record):
        """
        update progress on new record.
        """
        raise NotImplementedError

    def repr(self, progress):
        """
        human readble representation of a challenge progress
        """
        raise NotImplementedError
