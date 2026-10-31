class MeasurementNotFound(Exception):
    def __init__(self, message="Measurement not found"):
        self.message = message
        super().__init__(self.message)