```python
   def update_measurement_by_id(self, user: User, measurement_id: int, data: MeasurementUpdate) -> Measurement | None:
        query = select(Measurement).where(
            Measurement.user_id == user.id,
            Measurement.id == measurement_id
        )
        measurement = self.db.scalar(query)

        if measurement is None:
            return None

        if data.date is not None:
            # Vérifie que la date est bien un objet date
            if not isinstance(data.date, date):
                raise ValueError("Date invalide.")

            if data.date > date.today() or data.date < date(2020, 1, 1):
                raise ValueError("Date invalide.")

            measurement.date = data.date

        if data.weight_kg is not None:
            # Vérifie que le poids est dans une plage valide
            if not isinstance(data.weight_kg, (int, float)):
                raise ValueError("Poids invalide")

            if data.weight_kg <= 30 or data.weight_kg > 500:
                raise ValueError("Poids invalide")

            measurement.weight_kg = data.weight_kg

        self.db.commit()
        self.db.refresh(measurement)
        return measurement
```
