from sevencourts import *

from datetime import timedelta, datetime

# Period of of interchanging adjacent bookings display, in seconds
PERIOD_INTERCHANGE_ADJACENT_S = 10

TD_0_UPCOMING = timedelta(minutes = -5)
TD_1_WELCOME = timedelta(minutes = 2)
TD_3_COUNTDOWN = TD_0_UPCOMING # these two should be equal
TD_4_GAMEOVER = timedelta(minutes = 2)

def booking_player(player):
    txt = ''
    if player:
        firstname = player.get('firstname')
            
        if firstname:
            txt = firstname
        else:
            lastname = player.get('lastname')
            if lastname:
                if txt:
                    txt += ' '
                txt += lastname
            else:
                txt = _('booking.guest')
    return txt

def booking_team(booking, isTeam1=True):
    txt = ''
    tp1 =  booking.get('p1') if isTeam1 else booking.get('p3')
    if tp1:
        txt = booking_player(tp1)
    tp2 =  booking.get('p2') if isTeam1 else booking.get('p4')
    if tp2:
        if txt:
            txt += ' '
        txt = (txt or '') + booking_player(tp2)
    return txt

def is_current_second_in_period(period_seconds: int = 60, time_now = datetime.now()) -> bool:
    '''
    Returns true if the current time second is in the specified period.
    '''
    return (time_now.second // period_seconds) % 2 == 0


def truncate_to_tuple(text: str, max_length: int) -> tuple[str, str]:
    row_1 = row_2 = ''
    for wrd in text.split():
        if row_1:
            if len(row_1 + ' ' + wrd) <= max_length:
                row_1 += ' ' + wrd
            else:
                row_2 += (' ' if row_2 else '') + wrd
        else:
            row_1 = wrd
    return (row_1, row_2)


def booking_info_texts(booking, w_max_px, font) -> tuple[str, str]:
    row_1 = row_2 = ''

    max_length = max_string_length_for_font(font, w_max_px)

    no_person_name_booking_types = {'training', 'verbandspiel'} # TODO review, localize, etc.
    booking_type = booking.get('booking-type', '')
        
    if booking.get('display-text'):
        (row_1, row_2) = truncate_to_tuple(booking.get('display-text'), max_length)
    elif booking_type.lower() in no_person_name_booking_types and \
            not (booking.get('p2') or booking.get('p3') or booking.get('p4')):
        (row_1, row_2) = truncate_to_tuple(booking.get('booking-type'), max_length)
    elif (booking.get('p3') or booking.get('p4')):
        row_1 = booking_team(booking, True)
        row_2 = booking_team(booking, False)
    else:
        row_1 = booking_player(booking.get('p1'))
        row_2 = booking_player(booking.get('p2'))
    return (ellipsize(row_1, max_length), ellipsize(row_2, max_length))