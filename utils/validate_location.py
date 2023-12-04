AVG_LAT = 12.83849392
AVG_LON = 77.66468718


def is_in_class(lat, lon, accuracy):
    # return True
    return (
        accuracy >= 10 and abs(AVG_LAT - lat) < 0.00012 and abs(AVG_LON - lon) < 0.00015
    )
