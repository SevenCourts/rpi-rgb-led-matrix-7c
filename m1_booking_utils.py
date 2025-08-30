from sevencourts import *

from datetime import timedelta, datetime

# Period of of interchanging adjacent bookings display, in seconds
PERIOD_INTERCHANGE_ADJACENT_S = 10

TD_1_WELCOME = timedelta(minutes = 2)
TD_3_COUNTDOWN = TD_0_UPCOMING = timedelta(minutes = -5) # these two should be equal
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
                txt = lastname
            else:
                txt = _('booking.guest')
                txt = '' # FIXME guests?
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


def booking_info_texts(booking, w_max_px, font: graphics.Font) -> tuple[str, str]:
    row_1 = row_2 = ''

    
    max_length = max_string_length_for_font(font, w_max_px)

    # FIXME should be given by extra Booking API? #is_display_p1_name
    no_person_name_booking_types = {'Training', 'Verbandspiel'}#, 'Mit Ballmaschine'}
        
    text = ''
    if booking.get('display-text'):
        text = booking.get('display-text')        
    elif booking.get('booking-type', '') in no_person_name_booking_types and \
            not (booking.get('p2') or booking.get('p3') or booking.get('p4')):
        text = booking.get('booking-type')        
    elif (booking.get('p3') or booking.get('p4')):
        text = booking_team(booking, True) + ' ' + booking_team(booking, False)
    else:
        text = booking_player(booking.get('p1')) + ' ' + booking_player(booking.get('p2'))
    
    row_1, row_2 = truncate_text(text.strip(), max_length, ellipsize=True)

    return (ellipsize_text(row_1, max_length), ellipsize_text(row_2, max_length))


def hours_minutes_diff(t1: datetime, t2: datetime) -> tuple[int, int, int]:
    seconds_left = (t1 - t2).seconds - 1
    minutes_in_hour_left = seconds_left // 60 % 60 + 1
    hours_left = seconds_left // (60 * 60)
    return (hours_left, minutes_in_hour_left)


def acronym(text: str) -> str:
    return ''.join(word[0].upper() for word in text.split() if word)