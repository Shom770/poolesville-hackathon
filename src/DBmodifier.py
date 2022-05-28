class DBModifier():

    def __init__(self, engine, session, connection):
        self.engine = engine
        self.session = session
        self.connection = connection

