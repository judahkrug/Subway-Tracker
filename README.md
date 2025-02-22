# NYC Subway Tracker LED Display

A CircuitPython project that displays real-time NYC subway arrival times on an LED matrix board. The display shows upcoming trains at nearby stations, including the L train (1st Ave), R/W/N/Q trains (8th Street), and 4/6 trains (Astor Place).

![Version 1 Demo](https://github.com/judahkrug/Subway-Tracker/Tracker.gif)
- Since this demo - new features have been added (shown below)

## Features

- Real-time subway arrival information from MTA's API
- Displays train line, destination, and minutes until arrival
- Color-coded display matching official MTA line colors
- Smart pagination to show multiple upcoming trains
- Color-coded arrival times (red for longer waits)
- Automatic time synchronization
- Error handling with automatic reset after multiple failures

## Hardware Requirements

- LED Matrix Display (compatible with Adafruit MatrixPortal)
- Adafruit MatrixPortal or compatible microcontroller
- Power supply
- USB cable for programming

## Software Requirements

- CircuitPython
- Required Libraries:
  - adafruit_display_text
  - adafruit_bitmap_font
  - adafruit_matrixportal
  - adafruit_datetime

## Installation

1. Install CircuitPython on your MatrixPortal board
2. Copy the following files to your board:
   - code.py
   - g-dashboard.bmp (background image)
   - fonts/siji_with_6x10.bdf
3. Install required libraries in the lib directory
4. Power up the board

## How It Works

### Data Sources
The project fetches data from multiple subway stations:
- First Avenue (L train)
- Astor Place (6 train)
- 8th Street (R/W/N/Q trains)

### Display Logic
- Updates every 4 seconds
- Shows up to 7 upcoming trains across 3 pages
- Each train display includes:
  - Train line (in official MTA colors)
  - Destination
  - Minutes until arrival
- Time colors:
  - Normal: Green
  - Extended wait: Red
    - L train: ≥7 minutes
    - 4/6 trains: ≥9 minutes
    - R/W/N/Q trains: ≥10 minutes

### Features
1. **Smart Train Sorting**: Combines and sorts trains from multiple stations by arrival time
2. **Minimum Time Thresholds**: 
   - First Ave: 6 minutes
   - Astor Place: 8 minutes
   - 8th Street: 9 minutes
3. **Auto-Pagination**: Rotates through upcoming trains every 8 seconds
4. **Time Sync**: Resynchronizes clock every 120 seconds
5. **Error Recovery**: Automatically resets after 8 consecutive errors

## Configuration

Key constants that can be modified:
```python
UPDATE_DELAY = 4        # Seconds between data updates
REFRESH_DELAY = 8       # Seconds between page rotations
SYNC_TIME_DELAY = 120   # Seconds between time syncs
```

## Customization

The display uses custom colors for each train line:
- F train: Orange (#FF6319)
- L train: Gray (#A7A9AC)
- 4/6 trains: Green (#00933C)
- R/W/N/Q trains: Yellow (#FCCC0A)

## Contributing

Feel free to submit issues and enhancement requests!


## Acknowledgments

- Data provided by [jonthornton/MTAPI](https://github.com/jonthornton/MTAPI)
- Built using [Adafruit MatrixPortal](https://www.adafruit.com/product/4745) hardware
