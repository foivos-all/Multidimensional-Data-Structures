class airport:
    def __init__(self, airport_ID, name, city, country, IATA, ICAO, latitude, longitude, altitude, timezone, DST, TZ_database_time_zone):
        self.airport_ID = airport_ID
        self.name = name
        self.city = city
        self.country = country
        self.IATA = IATA
        self.ICAO = ICAO
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timezone = timezone
        self.DST = DST
        self.TZ_database_time_zone = TZ_database_time_zone