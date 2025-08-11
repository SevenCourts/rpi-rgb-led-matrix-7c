from sevencourts import *

import requests
import m1_booking_ebusy_single
import m1_booking_ebusy_vertical
import m1_booking_ebusy_grid

court_1 = {
            'court': {'id': 1, 'name': 'CUPRA Court präsentiert von Casa Automobile'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00', 
                'display-text': 'Verbandspiel H1 gg. TC Rechberghausen-Birenbach', 
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 'p2': None, 'p3': None, 'p4': None},
            'next': {
                'start-date': '2025-07-17T14:00:00+04:00',
                'end-date': '2025-07-17T14:30:00+04:00', 
                'display-text': '', 
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 
                'p2': {'firstname': 'Roman', 'lastname': 'Churkov'}, 
                'p3': None, 'p4': None}}
court_2 = {
            'court': {'id': 2, 'name': 'BBG Court'},
            'past': None,
            'current': None,
            'next': None}

court_3 = {
            'court': {'id': 3, 'name': 'EKW'},
            'past': None,
            'current': {
                'start-date': '2025-07-17T13:30:00+04:00',
                'end-date': '2025-07-17T14:00:00+04:00', 
                'display-text': 'Training H1',
                'p1': {'firstname': 'Ilya', 'lastname': 'Shinkarenko'}, 'p2': None, 'p3': None, 'p4': None},
            'next': None}
court_4 = {
            'court': {'id': 4, 'name': 'Ballwand'},
            'past': None,
            'current': None,
            'next': None}

_dev_timestamp = '2025-07-17T13:58:16+04:00'

booking_info_1_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_1,)} # ! trailing comma is important for tuple declaration
booking_info_2_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_1, court_2)}
booking_info_3_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_1, court_2, court_3)}
booking_info_4_courts = {
    '_dev_timestamp': _dev_timestamp,
    'courts': (court_1, court_2, court_3, court_4)}

def draw_booking(cnv, booking_info, panel_tz):

    booking_info = booking_info_3_courts

    total_courts = len(booking_info['courts'])
    logger.info(f"TOTAL COURTS: {total_courts}")
    if total_courts == 1:
        m1_booking_ebusy_single.draw(cnv, booking_info, panel_tz)
    else:
        m1_booking_ebusy_vertical.draw(cnv, booking_info, panel_tz)
        # m1_booking_ebusy_grid.draw(cnv, booking_info, panel_tz)

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
        