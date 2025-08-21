from sevencourts import *

import requests
import m1_booking_ebusy_single
import m1_booking_ebusy_vertical
from datetime import datetime
from m1_club_styles import *

style_TABB = ClubStyle(
    logo=LogoStyle(path='images/logos/TABB/tabb-logo-transparent-60x13-border-3.png'),
    ci=ClubCI(color_1=COLOR_CI_TABB_1, color_2=COLOR_CI_TABB_2),
    bookings=BookingStyle(is_weather_displayed=True, is_court_name_acronym=False)
)

style_SV1845 = ClubStyle(
    logo=LogoStyle(path='images/logos/SV1845/sv1845_76x64_eBusy_demo_logo.png', round_corners=True),
    ci=ClubCI(color_1=COLOR_CI_SV1845_1, color_2=COLOR_CI_SV1845_2),
    bookings=BookingStyle(is_weather_displayed=True, is_court_name_acronym=True)
)
 
court_TABB_1 = {
            'court': {'id': 1, 'name': 'CUPRA Court präsentiert von Casa Automobile'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00', 
                'display-text': '',
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'},
                'p2': {'firstname': 'Roman', 'lastname': 'Churkov'}, 
                'p3': {'firstname': 'Mario', 'lastname': 'Lopez'}, 
                'p4': {'firstname': 'Alexander', 'lastname': 'Drachnev'},
            },
            'next': {
                'start-date': '2025-07-17T14:00:00+04:00',
                'end-date': '2025-07-17T14:30:00+04:00', 
                'display-text': 'H1 Training', 
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'},
                'p2': None, 
                'p3': None, 
                'p4': None}}
court_TABB_2 = {
            'court': {'id': 2, 'name': 'BBG Court'},
            'past': None,
            'current': None,
            'next': None}

court_TABB_3 = {
            'court': {'id': 3, 'name': 'EKW'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00',
                'display-text': 'Verbandspiel H1 gg. TC Rechberghausen-Birenbach',
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 'p2': None, 'p3': None, 'p4': None},
            'next': None}



court_SV1845_1 = {
            'court': {'id': 1, 'name': 'Platz 1'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00', 
                'display-text': '',
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'},
                'p2': {'firstname': 'Roman', 'lastname': 'Churkov'}, 
                'p3': {'firstname': 'Mario', 'lastname': 'Lopez'}, 
                'p4': {'firstname': 'Alexander', 'lastname': 'Drachnev'},
            },
            'next': {
                'start-date': '2025-07-17T14:00:00+04:00',
                'end-date': '2025-07-17T14:30:00+04:00', 
                'display-text': 'H1 Training', 
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'},
                'p2': None, 
                'p3': None, 
                'p4': None}}
court_SV1845_2 = {
            'court': {'id': 2, 'name': 'Platz 2'},
            'past': None,
            'current': None,
            'next': None}

court_SV1845_3 = {
            'court': {'id': 3, 'name': 'Platz 3'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00',
                'display-text': 'Verbandspiel H1 gg. TC Rechberghausen-Birenbach',
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 'p2': None, 'p3': None, 'p4': None},
            'next': None}
court_SV1845_4 = {
            'court': {'id': 4, 'name': 'Platz 4'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:58:15+04:00',
                'display-text': '',
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 'p2': None, 'p3': None, 'p4': None},
            'next': None}

_dev_timestamp = '2025-07-17T13:58:16+04:00'
# _dev_timestamp = '2025-07-17T13:58:14+04:00'
#_dev_timestamp = None

booking_TABB_1_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_TABB_1,)} # ! trailing comma is important for tuple declaration
booking_TABB_2_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_TABB_1, court_TABB_2)}
booking_TABB_3_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_TABB_1, court_TABB_2, court_TABB_3)}

booking_SV1845_4_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_SV1845_1, court_SV1845_2, court_SV1845_3, court_SV1845_4)}

def draw_booking(cnv, booking_info, weather_info, panel_tz):

    t = datetime.now()
    period_seconds = 10
    if (t.second // period_seconds) % 2 == 0:
        style = style_SV1845        
    else:
        style = style_TABB

    total_courts = len(booking_info.get('courts', []))
    if total_courts == 0:
        #logger.warning(f"No courts in booking info: {booking_info}")
        draw_text(cnv, 0, 10, "Please select court/s")        
    elif total_courts == 1:
        m1_booking_ebusy_single.draw(cnv, booking_info, panel_tz, style)
    else:
        m1_booking_ebusy_vertical.draw(cnv, booking_info, weather_info, panel_tz, style)

def draw_ebusy_ads(cnv, ebusy_ads):
    id = ebusy_ads.get("id")
    url = ebusy_ads.get("url")
    path = IMAGE_CACHE_DIR + "/ebusy_" + str(id)

    try:
        if (os.path.isfile(path)):
            image = Image.open(path)
        else:
            image = Image.open(requests.get(url, stream=True).raw)            
            image.save(path, 'png')

        x = (W_PANEL - image.width) / 2
        y = (H_PANEL - image.height) / 2
        cnv.SetImage(image.convert('RGB'), x, y)

    except Exception as e:
        logger.debug(f"Error downloading image {url}", e)
        logger.exception(e)
        