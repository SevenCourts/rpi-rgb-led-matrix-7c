_court_TABB_1 = {
    "court": {"id": 1, "name": "CUPRA Court präsentiert von Casa Automobile"},
    "past": None,
    "current": {
        "start-date": "2025-07-17T13:30:00+04:00",
        "end-date": "2025-07-17T14:00:00+04:00",
        "display-text": "",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": {"firstname": "Roman", "lastname": "Churkov"},
        "p3": {"firstname": "Mario", "lastname": "Lopez"},
        "p4": {"firstname": "Alexander", "lastname": "Drachnev"},
    },
    "next": {
        "start-date": "2025-07-17T14:00:00+04:00",
        "end-date": "2025-07-17T14:30:00+04:00",
        "display-text": "H1 Training",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": None,
        "p3": None,
        "p4": None,
    },
}
_court_TABB_2 = {
    "court": {"id": 2, "name": "BBG Court"},
    "past": None,
    "current": None,
    "next": None,
}

_court_TABB_3 = {
    "court": {"id": 3, "name": "EKW"},
    "past": None,
    "current": {
        "start-date": "2025-07-17T13:30:00+04:00",
        "end-date": "2025-07-17T14:00:00+04:00",
        "display-text": "Verbandspiel H1 gg. TC Rechberghausen-Birenbach",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": None,
        "p3": None,
        "p4": None,
    },
    "next": None,
}

_court_SV1845_1 = {
    "court": {"id": 1, "name": "Platz 1"},
    "past": None,
    "current": {
        "start-date": "2025-07-17T13:30:00+04:00",
        "end-date": "2025-07-17T14:00:00+04:00",
        "display-text": "",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": {"firstname": "Roman", "lastname": "Churkov"},
        "p3": {"firstname": "Mario", "lastname": "Lopez"},
        "p4": {"firstname": "Alexander", "lastname": "Drachnev"},
    },
    "next": {
        "start-date": "2025-07-17T14:00:00+04:00",
        "end-date": "2025-07-17T14:30:00+04:00",
        "display-text": "H1 Training",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": None,
        "p3": None,
        "p4": None,
    },
}
_court_SV1845_2 = {
    "court": {"id": 2, "name": "Platz 2"},
    "past": None,
    "current": None,
    "next": None,
}

_court_SV1845_3 = {
    "court": {"id": 3, "name": "Platz 3"},
    "past": None,
    "current": {
        "start-date": "2025-07-17T13:30:00+04:00",
        "end-date": "2025-07-17T14:00:00+04:00",
        "display-text": "Verbandspiel H1 gg. TC Rechberghausen-Birenbach",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": None,
        "p3": None,
        "p4": None,
    },
    "next": None,
}
_court_SV1845_4 = {
    "court": {"id": 4, "name": "Platz 4"},
    "past": None,
    "current": {
        "start-date": "2025-07-17T13:30:00+04:00",
        "end-date": "2025-07-17T14:58:15+04:00",
        "display-text": "",
        "p1": {"firstname": "Ilya", "lastname": "Shinkarenko"},
        "p2": None,
        "p3": None,
        "p4": None,
    },
    "next": None,
}

_dev_timestamp = "2025-07-17T13:58:16+04:00"
# _dev_timestamp = '2025-07-17T13:58:14+04:00'
# _dev_timestamp = None

_booking_TABB_1_courts = {
    "_dev_timestamp": _dev_timestamp,
    "courts": (_court_TABB_1,),
}  # ! trailing comma is important for tuple declaration
_booking_TABB_2_courts = {
    "_dev_timestamp": _dev_timestamp,
    "courts": (_court_TABB_1, _court_TABB_2),
}
_booking_TABB_3_courts = {
    "_dev_timestamp": _dev_timestamp,
    "courts": (_court_TABB_1, _court_TABB_2, _court_TABB_3),
}
_booking_SV1845_4_courts = {
    "_dev_timestamp": _dev_timestamp,
    "courts": (_court_SV1845_1, _court_SV1845_2, _court_SV1845_3, _court_SV1845_4),
}
