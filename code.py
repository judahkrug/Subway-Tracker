import time
import microcontroller
from board import NEOPIXEL
import displayio
import adafruit_display_text.label
from adafruit_datetime import datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network

first_ave_source = 'https://api.wheresthefuckingtrain.com/by-id/L06'
second_ave_source = 'https://api.wheresthefuckingtrain.com/by-id/F14'
astor_pl_source = 'https://api.wheresthefuckingtrain.com/by-id/636'
eight_street_source = 'https://api.wheresthefuckingtrain.com/by-id/R21'

DATA_LOCATION = ["data"]

# Delay in seconds before fetching new data (Processing takes 3-5 seconds)
UPDATE_DELAY = 4

# Delay in seconds before displaying new trains
REFRESH_DELAY = 8

# Delay in time before resyncing clock
SYNC_TIME_DELAY = 120

# Later can change background image for any constant pixel values
BACKGROUND_IMAGE = 'g-dashboard.bmp'


ERROR_RESET_THRESHOLD = 8


def get_arrival_in_seconds_from_now(currTime, date_str):
    train_date = datetime.fromisoformat(date_str).replace(tzinfo=None) # Remove tzinfo to be able to diff dates
    return max(0, (train_date-currTime).total_seconds())

def sort_NS_trains(northbound_trains, southbound_trains, currTime, minTime):
    print ("Sorting N/S Trains")
    sorted_trains = []
    i, j = 0, 0
    len1 = len(northbound_trains)
    len2 = len(southbound_trains)

    while i < len1 and j < len2:
        if northbound_trains[i]['time'] < southbound_trains[j]['time']:
            northbound_trains[i]['time'] = get_arrival_in_seconds_from_now(currTime, northbound_trains[i]['time'])
            northbound_trains[i]['dir'] = 'N'
            if (northbound_trains[i]['time'] >= minTime):
                sorted_trains.append(northbound_trains[i])
            i = i+1
        else:
            southbound_trains[j]['time'] = get_arrival_in_seconds_from_now(currTime, southbound_trains[j]['time'])
            southbound_trains[j]['dir'] = 'S'
            if (southbound_trains[j]['time'] >= minTime):
                sorted_trains.append(southbound_trains[j])
            j = j+1

    while i < len1:
        northbound_trains[i]['time'] = get_arrival_in_seconds_from_now(currTime, northbound_trains[i]['time'])
        northbound_trains[i]['dir'] = 'N'
        if (northbound_trains[i]['time'] >= minTime):
            sorted_trains.append(northbound_trains[i])
        i = i+1

    while j < len2:
        southbound_trains[j]['time'] = get_arrival_in_seconds_from_now(currTime, southbound_trains[j]['time'])
        southbound_trains[j]['dir'] = 'S'
        if (southbound_trains[j]['time'] >= minTime):
            sorted_trains.append(southbound_trains[j])
        j = j+1

    return sorted_trains

def sort_trains(train1, train2, currTime):
    sorted_trains = []
    i, j = 0, 0
    len1 = len(train1)
    len2 = len(train2)

    while i < len1 and j < len2:
        if train1[i]['time'] < train2[j]['time']:
            sorted_trains.append(train1[i])
            i = i+1
        else:
            sorted_trains.append(train2[j])
            j = j+1
        # Stop once 7 trains are added
        if (i + j >= 7):
            return sorted_trains
    sorted_trains = sorted_trains + train1[i:] + train2[j:]
    return sorted_trains

def get_arrival_times():
    currTime = datetime.now()

    print("Fetching first_ave_trains")
    first_ave_min_time = 360
    first_ave_trains = network.fetch_data(first_ave_source, json_path=(DATA_LOCATION,))
    first_ave_trains = sort_NS_trains(first_ave_trains[0]['N'], first_ave_trains[0]['S'], currTime, first_ave_min_time)

    # print("Fetching second_ave_trains")
    # second_ave_trains = network.fetch_data(second_ave_source, json_path=(DATA_LOCATION,))
    # second_ave_trains = sort_NS_trains(second_ave_trains[0]['N'], second_ave_trains[0]['S'], currTime)

    print("Fetching astor_pl_trains")
    astor_pl_min_time = 480
    astor_pl_trains = network.fetch_data(astor_pl_source, json_path=(DATA_LOCATION,))
    astor_pl_trains = sort_NS_trains(astor_pl_trains[0]['N'], astor_pl_trains[0]['S'], currTime, astor_pl_min_time)

    print("Fetching eight_street_trains")
    eight_street_min_time = 540
    eight_street_trains = network.fetch_data(eight_street_source, json_path=(DATA_LOCATION,))
    eight_street_trains = sort_NS_trains(eight_street_trains[0]['N'], eight_street_trains[0]['S'], currTime, eight_street_min_time)

    trains = sort_trains(sort_trains(first_ave_trains, eight_street_trains, currTime), astor_pl_trains, currTime)

    # Ensure only using first 7 trains
    trains = trains[:7]
    print("FINAL TRAINS")
    print(trains)

    # Cleanup trains for printing
    for train in trains:
        if train['dir'] == 'N':
            if train['route'] == 'L':
                train['dir1'] = '8TH'
                train['dir2'] = 'AVE'
                train['color'] = 3
            if train['route'] == 'F':
                train['dir1'] = 'JAMAICA'
                train['dir2'] = ''
                train['color'] = 0
            if train['route'] == '6':
                train['dir1'] = 'PELHAM'
                train['dir2'] = ''
                train['color'] = 4
            if train['route'] == '4':
                train['dir1'] = 'WOODLN'
                train['dir2'] = ''
                train['color'] = 4
            if train['route'] == 'R':
                train['dir1'] = 'FRST'
                train['dir2'] = 'HLS'
                train['color'] = 5
            if train['route'] == 'W':
                train['dir1'] = 'ASTORIA'
                train['dir2'] = ''
                train['color'] = 5
            if train['route'] == 'N':
                train['dir1'] = 'ASTORIA'
                train['dir2'] = ''
                train['color'] = 5
            if train['route'] == 'Q':
                train['dir1'] = '96TH'
                train['dir2'] = 'ST'
                train['color'] = 5
        else:
            if train['route'] == 'L':
                train['dir1'] = 'BKLYN'
                train['dir2'] = ''
                train['color'] = 3
            if train['route'] == 'F':
                train['dir1'] = 'CONEY'
                train['dir2'] = 'IS'
                train['color'] = 0
            if train['route'] == '6':
                train['dir1'] = 'BKLYN'
                train['dir2'] = ''
                train['color'] = 4
            if train['route'] == '4':
                train['dir1'] = 'NEW'
                train['dir2'] = 'LOTS'
                train['color'] = 4
            if train['route'] == 'R':
                train['dir1'] = '95TH'
                train['dir2'] = 'ST'
                train['color'] = 5
            if train['route'] == 'W':
                train['dir1'] = 'S'
                train['dir2'] = 'FERRY'
                train['color'] = 5
            if train['route'] == 'N':
                train['dir1'] = 'CONEY'
                train['dir2'] = 'IS'
                train['color'] = 5
            if train['route'] == 'Q':
                train['dir1'] = 'CONEY'
                train['dir2'] = 'IS'
                train['color'] = 5

    return trains

def modify_lines(train, index):
        route = train['route']
        color = colors[train['color']]
        dir1 = train['dir1']
        dir2 = train['dir2']
        time = train['time']

        time = str(round((time) / 60.0))

        text_lines[index].text = route
        text_lines[index].color = color
        text_lines[1 + index].text = dir1
        text_lines[1 + index].color = colors[1]
        text_lines[1 + index].x = 7
        text_lines[2 + index].text = dir2
        text_lines[2 + index].color = colors[1]
        text_lines[2 + index].x = ((len(dir1) * 6) + 9)
        text_lines[3 + index].text = time

        if ((route == 'R' or route == 'W' or route == 'N' or route == 'Q') and int(time) >= 10):
            text_lines[3 + index].color = colors[6]
        elif (route == 'L' and int(time) >= 7):
            text_lines[3 + index].color = colors[6]
        elif ((route == '4' or route == '6' ) and int(time) >= 9):
            text_lines[3 + index].color = colors[6]
        else:
            text_lines[3 + index].color = colors[7]

        if len(time) == 1:
            text_lines[3 + index].x = 59
        else:
            text_lines[3 + index].x = 53

def clear_lines(index):
        text_lines[index].text = ""
        text_lines[1 + index].text = ""
        text_lines[2 + index].text = ""
        text_lines[3 + index].text = ""

def update_text(trains):

    size = len(trains)

    # Display Page 1 Train(1/2/3)
    if size >= 1:
        modify_lines(trains[0], 1)
    else:
        clear_lines(1)
        clear_lines(5)
        clear_lines(9)

    if size >= 3:
        modify_lines(trains[1], 5)
        modify_lines(trains[2], 9)
    elif size >= 2:
        modify_lines(trains[1], 5)
        clear_lines(9)
    else:
        clear_lines(5)
        clear_lines(9)

    display.show(group)


    # Display Page 2 (Train 1/4/5)
    if size >= 5:
        trains[3]['time'] += REFRESH_DELAY
        trains[4]['time'] += REFRESH_DELAY
        time.sleep(REFRESH_DELAY)
        modify_lines(trains[3], 5)
        modify_lines(trains[4], 9)
    elif size >= 4:
        trains[3]['time'] += REFRESH_DELAY
        time.sleep(REFRESH_DELAY)
        modify_lines(trains[3], 5)
        clear_lines(9)


    # Display Page 3 (Train 1/6/7)
    if size >= 7:
        trains[5]['time'] += (2 * REFRESH_DELAY)
        trains[6]['time'] += (2 * REFRESH_DELAY)
        time.sleep(REFRESH_DELAY)
        modify_lines(trains[5], 5)
        modify_lines(trains[6], 9)
    elif size >= 6:
        trains[5]['time'] += (2 * REFRESH_DELAY)
        time.sleep(REFRESH_DELAY)
        modify_lines(trains[5], 5)
        clear_lines(9)


# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
bitmap = displayio.OnDiskBitmap(open(BACKGROUND_IMAGE, 'rb'))
colors = [0xff6319, 0xffffff, 0xDD8000, 0xa7a9ac, 0x00933c, 0xfccc0a, 0x00933c, 0xFF0000]
#         F         Text      Number    L         46        RWNQ      Green     RED
font = bitmap_font.load_font("fonts/siji_with_6x10.bdf")

text_lines = [
    displayio.TileGrid(bitmap, pixel_shader=getattr(bitmap, 'pixel_shader', displayio.ColorConverter())),
    adafruit_display_text.label.Label(font, color=colors[0], x=0, y=3, text=""),
    adafruit_display_text.label.Label(font, color=0x7EC8E3, x=23, y=3, text="FUN"),
    adafruit_display_text.label.Label(font, color=colors[1], x=38, y=3, text=""),
    adafruit_display_text.label.Label(font, color=colors[2], x=53, y=3, text=""),
    adafruit_display_text.label.Label(font, color=colors[0], x=0, y=15, text=""),
    adafruit_display_text.label.Label(font, color=0x7EC8E3, x=20, y=15, text="CITY"),
    adafruit_display_text.label.Label(font, color=colors[1], x=21, y=15, text=""),
    adafruit_display_text.label.Label(font, color=colors[2], x=53, y=15, text=""),
    adafruit_display_text.label.Label(font, color=colors[0], x=0, y=27, text=""),
    adafruit_display_text.label.Label(font, color=colors[7], x=11, y=27, text="STATION"),
    adafruit_display_text.label.Label(font, color=colors[1], x=31, y=27, text=""),
    adafruit_display_text.label.Label(font, color=colors[2], x=53, y=27, text=""),
]
for x in text_lines:
    group.append(x)
display.show(group)

error_counter = 0
last_time_sync = None
while True:
    try:
        if last_time_sync is None or time.monotonic() > last_time_sync + SYNC_TIME_DELAY:
            # Sync clock to minimize time drift
            network.get_local_time()
            last_time_sync = time.monotonic()
        trains = get_arrival_times()
        update_text(trains)
    # except (ValueError, RuntimeError) as e:
    except Exception as e:
        print("Some error occured, retrying! -", e)
        error_counter = error_counter + 1
        if error_counter > ERROR_RESET_THRESHOLD:
            microcontroller.reset()

    time.sleep(UPDATE_DELAY)
