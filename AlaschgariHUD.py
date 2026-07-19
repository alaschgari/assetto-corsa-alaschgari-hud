# AlaschgariHUD for Assetto Corsa
# Modular Sidekick Replica HUD - Floating widgets with rounded corners & custom colors

import ac
import acsys
import sys
import os
import math

# Inject stdlib for stripped Assetto Corsa python environment
if sys.maxsize > 2**32:
    sysdir = os.path.join(os.path.dirname(__file__), 'stdlib64')
else:
    sysdir = os.path.join(os.path.dirname(__file__), 'stdlib')

sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

import traceback

# Global Debug label
lblDebugError = 0

def log_error(msg):
    global lblDebugError
    try:
        path = os.path.join(os.path.dirname(__file__), 'error.log')
        with open(path, 'a') as f:
            f.write(msg + "\n")
        if lblDebugError != 0:
            lines = [l for l in msg.split('\n') if l.strip()]
            last_line = lines[-1] if lines else "Unknown Error"
            ac.setText(lblDebugError, "ERR: " + last_line[:65])
    except:
        pass

# Clear log at startup
try:
    path = os.path.join(os.path.dirname(__file__), 'error.log')
    if os.path.exists(path):
        os.remove(path)
except:
    pass

try:
    from third_party.sim_info import SimInfo
    simInfo = None
    try:
        simInfo = SimInfo()
    except Exception as e:
        log_error("SimInfo init failed: " + str(e))
except Exception as e:
    log_error("SimInfo import failed: " + traceback.format_exc())

# App configuration
appName = "AlaschgariHUD"
width, height = 800, 140

# Color Palettes
BG_COLORS = [
    [0.08, 0.09, 0.12], # 0: Dark Blue (Default)
    [0.02, 0.02, 0.02], # 1: Pitch Black
    [0.15, 0.15, 0.15], # 2: Dark Grey
    [0.06, 0.04, 0.10]  # 3: Cyber Violet
]

TEXT_COLORS = [
    [0.0, 0.94, 1.0, 1.0],  # 0: Neon Cyan
    [1.0, 0.0, 0.62, 1.0],  # 1: Neon Pink
    [1.0, 1.0, 1.0, 1.0],   # 2: Crisp White
    [0.0, 1.0, 0.4, 1.0],   # 3: Toxic Green
    [1.0, 1.0, 0.0, 1.0]    # 4: Bright Yellow
]

# Settings variables with defaults
scale = 1.0
show_rpm = True
show_chassis = True
show_tire_bars = True
bg_color_idx = 0
opacity_pct = 65
text_color_idx = 0

# App Windows
appShift = 0
appTires = 0
appSpeed = 0
appPedals = 0
appKers = 0
appTimes = 0
appFuel = 0
appSettings = 0

# UI Controls per app window
# Tires App
lblPressFL = 0
lblPressFR = 0
lblPressRL = 0
lblPressRR = 0
lblBrakeF = 0
lblBrakeR = 0

# Speed App
lblSpeed = 0
lblSpeedLabel = 0
lblGear = 0
lblGearLabel = 0
lblGForce = 0

# Pedals App
lblPedalClutch = 0
lblPedalBrake = 0
lblPedalThrottle = 0
lblPedalClutchVal = 0
lblPedalBrakeVal = 0
lblPedalThrottleVal = 0

# KERS & Wear App
lblKersName = 0
lblWearName = 0

# Times App
lblTimesCurrent = 0
lblTimesBest = 0
lblTimesLast = 0
lblTimesLaps = 0

# Fuel App
lblFuelCurrent = 0
lblFuelCons = 0
lblFuelEst = 0
lblFuelTemps = 0

# Settings App
lblSliderName = 0
sliderScale = 0
lblOpacityName = 0
sliderOpacity = 0
lblBgColorName = 0
sliderBgColor = 0
lblTextColorName = 0
sliderTextColor = 0

# Telemetry data cache
gear = "G1"
speed = 0
rpms = 0
maxRpm = 0
tireTemps = [0.0, 0.0, 0.0, 0.0]
tirePressures = [0.0, 0.0, 0.0, 0.0]
brakeTemps = [0.0, 0.0, 0.0, 0.0]
clutchInput = 0.0
brakeInput = 0.0
throttleInput = 0.0
gForceLat = 0.0
gForceLon = 0.0
kersCharge = 1.0
tyreWear = 0.0

# Fuel Calculator State
last_lap_completed = -1
fuel_at_lap_start = -1.0
fuel_consumptions = []
fuel_per_lap_avg = 0.0

# Settings tracker variables
last_spinner_value = 100.0
last_opacity_value = 65.0
last_bg_color_value = 0.0
last_text_color_value = 0.0

def getConfigPath():
    return os.path.join(os.path.dirname(__file__), 'config.ini')

def loadConfig():
    global scale, show_rpm, show_chassis, show_tire_bars, bg_color_idx, opacity_pct, text_color_idx
    path = getConfigPath()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k == 'scale':
                            try:
                                scale = float(v) / 100.0
                                if scale < 0.5: scale = 0.5
                                if scale > 1.5: scale = 1.5
                            except:
                                scale = 1.0
                        elif k == 'show_rpm':
                            show_rpm = (v.lower() == 'true')
                        elif k == 'show_chassis':
                            show_chassis = (v.lower() == 'true')
                        elif k == 'show_tire_bars':
                            show_tire_bars = (v.lower() == 'true')
                        elif k == 'bg_color_idx':
                            try: bg_color_idx = int(v)
                            except: bg_color_idx = 0
                        elif k == 'opacity_pct':
                            try: opacity_pct = int(v)
                            except: opacity_pct = 65
                        elif k == 'text_color_idx':
                            try: text_color_idx = int(v)
                            except: text_color_idx = 0
        except Exception as e:
            log_error("loadConfig failed: " + str(e))

def saveConfig():
    try:
        path = getConfigPath()
        with open(path, 'w') as f:
            f.write("[SETTINGS]\n")
            f.write("scale = " + str(int(scale * 100)) + "\n")
            f.write("show_rpm = " + str(show_rpm) + "\n")
            f.write("show_chassis = " + str(show_chassis) + "\n")
            f.write("show_tire_bars = " + str(show_tire_bars) + "\n")
            f.write("bg_color_idx = " + str(bg_color_idx) + "\n")
            f.write("opacity_pct = " + str(opacity_pct) + "\n")
            f.write("text_color_idx = " + str(text_color_idx) + "\n")
    except Exception as e:
        log_error("saveConfig failed: " + str(e))

def applyTextColors():
    global text_color_idx, lblSpeed, lblGForce, lblPressFL, lblPressFR, lblPressRL, lblPressRR
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal, lblKersName, lblWearName
    global lblPedalClutch, lblPedalBrake, lblPedalThrottle
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    
    try:
        c = TEXT_COLORS[text_color_idx]
        labels = [
            lblSpeed, lblGForce, lblPressFL, lblPressFR, lblPressRL, lblPressRR,
            lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal,
            lblPedalClutch, lblPedalBrake, lblPedalThrottle, lblKersName, lblWearName,
            lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps,
            lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
        ]
        for lbl in labels:
            if lbl != 0:
                ac.setFontColor(lbl, c[0], c[1], c[2], c[3])
    except Exception as e:
        log_error("applyTextColors failed:\n" + traceback.format_exc())

def updateScale(new_scale):
    global scale
    global appShift, appTires, appSpeed, appPedals, appKers, appTimes, appFuel
    global lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR
    global lblSpeed, lblSpeedLabel, lblGear, lblGearLabel, lblGForce
    global lblPedalClutch, lblPedalBrake, lblPedalThrottle, lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblKersName, lblWearName
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps

    scale = new_scale
    
    # 1. Resize all modular windows
    ac.setSize(appShift, int(round(480 * scale)), int(round(20 * scale)))
    ac.setSize(appTires, int(round(310 * scale)), int(round(125 * scale)))
    ac.setSize(appSpeed, int(round(290 * scale)), int(round(125 * scale)))
    ac.setSize(appPedals, int(round(162 * scale)), int(round(70 * scale)))
    ac.setSize(appKers, int(round(162 * scale)), int(round(45 * scale)))
    ac.setSize(appTimes, int(round(162 * scale)), int(round(70 * scale)))
    ac.setSize(appFuel, int(round(162 * scale)), int(round(70 * scale)))

    # 2. Update Tires label positions and fonts
    ac.setPosition(lblPressFL, int(round(15 * scale)), int(round(22 * scale)))
    ac.setFontSize(lblPressFL, int(round(11 * scale)))
    ac.setPosition(lblPressRL, int(round(15 * scale)), int(round(72 * scale)))
    ac.setFontSize(lblPressRL, int(round(11 * scale)))
    ac.setPosition(lblPressFR, int(round(212 * scale)), int(round(22 * scale)))
    ac.setFontSize(lblPressFR, int(round(11 * scale)))
    ac.setPosition(lblPressRR, int(round(212 * scale)), int(round(72 * scale)))
    ac.setFontSize(lblPressRR, int(round(11 * scale)))
    ac.setPosition(lblBrakeF, int(round(265 * scale)), int(round(22 * scale)))
    ac.setFontSize(lblBrakeF, int(round(13 * scale)))
    ac.setPosition(lblBrakeR, int(round(265 * scale)), int(round(72 * scale)))
    ac.setFontSize(lblBrakeR, int(round(13 * scale)))

    # 3. Update Speed label positions and fonts
    ac.setPosition(lblSpeed, int(round(70 * scale)), int(round(42 * scale)))
    ac.setFontSize(lblSpeed, int(round(28 * scale)))
    ac.setPosition(lblSpeedLabel, int(round(70 * scale)), int(round(105 * scale)))
    ac.setFontSize(lblSpeedLabel, int(round(8 * scale)))
    ac.setPosition(lblGear, int(round(215 * scale)), int(round(34 * scale)))
    ac.setFontSize(lblGear, int(round(24 * scale)))
    ac.setPosition(lblGForce, int(round(215 * scale)), int(round(75 * scale)))
    ac.setFontSize(lblGForce, int(round(9 * scale)))
    ac.setPosition(lblGearLabel, int(round(215 * scale)), int(round(105 * scale)))
    ac.setFontSize(lblGearLabel, int(round(8 * scale)))

    # 4. Update Pedals label positions and fonts
    ac.setPosition(lblPedalClutch, int(round(8 * scale)), int(round(5 * scale)))
    ac.setFontSize(lblPedalClutch, int(round(8 * scale)))
    ac.setPosition(lblPedalBrake, int(round(8 * scale)), int(round(23 * scale)))
    ac.setFontSize(lblPedalBrake, int(round(8 * scale)))
    ac.setPosition(lblPedalThrottle, int(round(8 * scale)), int(round(41 * scale)))
    ac.setFontSize(lblPedalThrottle, int(round(8 * scale)))
    ac.setPosition(lblPedalClutchVal, int(round(154 * scale)), int(round(5 * scale)))
    ac.setFontSize(lblPedalClutchVal, int(round(8 * scale)))
    ac.setPosition(lblPedalBrakeVal, int(round(154 * scale)), int(round(23 * scale)))
    ac.setFontSize(lblPedalBrakeVal, int(round(8 * scale)))
    ac.setPosition(lblPedalThrottleVal, int(round(154 * scale)), int(round(41 * scale)))
    ac.setFontSize(lblPedalThrottleVal, int(round(8 * scale)))

    # 5. Update KERS label positions and fonts
    ac.setPosition(lblKersName, int(round(12 * scale)), int(round(16 * scale)))
    ac.setFontSize(lblKersName, int(round(9 * scale)))
    ac.setPosition(lblWearName, int(round(90 * scale)), int(round(16 * scale)))
    ac.setFontSize(lblWearName, int(round(9 * scale)))

    # 6. Update Times label positions and fonts
    ac.setPosition(lblTimesCurrent, int(round(81 * scale)), int(round(22 * scale)))
    ac.setFontSize(lblTimesCurrent, int(round(15 * scale)))
    ac.setPosition(lblTimesBest, int(round(8 * scale)), int(round(5 * scale)))
    ac.setFontSize(lblTimesBest, int(round(8 * scale)))
    ac.setPosition(lblTimesLast, int(round(154 * scale)), int(round(5 * scale)))
    ac.setFontSize(lblTimesLast, int(round(8 * scale)))
    ac.setPosition(lblTimesLaps, int(round(81 * scale)), int(round(50 * scale)))
    ac.setFontSize(lblTimesLaps, int(round(8 * scale)))

    # 7. Update Fuel label positions and fonts
    ac.setPosition(lblFuelCurrent, int(round(81 * scale)), int(round(22 * scale)))
    ac.setFontSize(lblFuelCurrent, int(round(14 * scale)))
    ac.setPosition(lblFuelCons, int(round(8 * scale)), int(round(5 * scale)))
    ac.setFontSize(lblFuelCons, int(round(8 * scale)))
    ac.setPosition(lblFuelEst, int(round(154 * scale)), int(round(5 * scale)))
    ac.setFontSize(lblFuelEst, int(round(8 * scale)))
    ac.setPosition(lblFuelTemps, int(round(81 * scale)), int(round(50 * scale)))
    ac.setFontSize(lblFuelTemps, int(round(8 * scale)))

def formatTime(ms):
    if ms <= 0:
        return "--:--.---"
    seconds = int(ms / 1000)
    milliseconds = int(ms % 1000)
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)
    return "{:d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)

def formatTimeShort(ms):
    if ms <= 0:
        return "--:--.-"
    seconds = int(ms / 1000)
    milliseconds = int(ms % 1000)
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)
    tenths = int(milliseconds / 100)
    return "{:d}:{:02d}.{:d}".format(minutes, seconds, tenths)

def acMain(ac_version):
    global scale, lblDebugError, bg_color_idx, opacity_pct, text_color_idx
    global appShift, appTires, appSpeed, appPedals, appKers, appTimes, appFuel, appSettings
    global lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR
    global lblSpeed, lblSpeedLabel, lblGear, lblGearLabel, lblGForce
    global lblPedalClutch, lblPedalBrake, lblPedalThrottle, lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblKersName, lblWearName
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    global lblSliderName, sliderScale, lblOpacityName, sliderOpacity, lblBgColorName, sliderBgColor, lblTextColorName, sliderTextColor
    global last_spinner_value, last_opacity_value, last_bg_color_value, last_text_color_value

    try:
        loadConfig()

        # ---------------------------------------------
        # 1. APP: SHIFT LIGHT BAR (480px x 20px)
        # ---------------------------------------------
        appShift = ac.newApp("AlaschgariHUD - Shift Lights")
        ac.setSize(appShift, int(round(480 * scale)), int(round(20 * scale)))
        ac.setTitle(appShift, "")
        ac.drawBorder(appShift, 0)
        ac.setBackgroundOpacity(appShift, 0.0)
        ac.setIconPosition(appShift, -10000, -10000)
        ac.addRenderCallback(appShift, drawShiftGL)

        # ---------------------------------------------
        # 2. APP: TIRES & BRAKES STATUS (310px x 125px)
        # ---------------------------------------------
        appTires = ac.newApp("AlaschgariHUD - Tires & Brakes")
        ac.setSize(appTires, int(round(310 * scale)), int(round(125 * scale)))
        ac.setTitle(appTires, "")
        ac.drawBorder(appTires, 0)
        ac.setBackgroundOpacity(appTires, 0.0)
        ac.setIconPosition(appTires, -10000, -10000)
        ac.addRenderCallback(appTires, drawTiresGL)

        # Labels
        lblPressFL = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressFL, int(round(15 * scale)), int(round(22 * scale)))
        ac.setFontSize(lblPressFL, int(round(11 * scale)))

        lblPressRL = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressRL, int(round(15 * scale)), int(round(72 * scale)))
        ac.setFontSize(lblPressRL, int(round(11 * scale)))

        lblPressFR = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressFR, int(round(212 * scale)), int(round(22 * scale)))
        ac.setFontSize(lblPressFR, int(round(11 * scale)))
        ac.setFontAlignment(lblPressFR, "right")

        lblPressRR = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressRR, int(round(212 * scale)), int(round(72 * scale)))
        ac.setFontSize(lblPressRR, int(round(11 * scale)))
        ac.setFontAlignment(lblPressRR, "right")

        lblBrakeF = ac.addLabel(appTires, "0")
        ac.setPosition(lblBrakeF, int(round(265 * scale)), int(round(22 * scale)))
        ac.setFontSize(lblBrakeF, int(round(13 * scale)))
        ac.setFontColor(lblBrakeF, 1.0, 0.2, 0.2, 1.0)

        lblBrakeR = ac.addLabel(appTires, "0")
        ac.setPosition(lblBrakeR, int(round(265 * scale)), int(round(72 * scale)))
        ac.setFontSize(lblBrakeR, int(round(13 * scale)))
        ac.setFontColor(lblBrakeR, 1.0, 0.2, 0.2, 1.0)

        # ---------------------------------------------
        # 3. APP: SPEEDOMETER & GEAR (290px x 125px)
        # ---------------------------------------------
        appSpeed = ac.newApp("AlaschgariHUD - Speed & Gear")
        ac.setSize(appSpeed, int(round(290 * scale)), int(round(125 * scale)))
        ac.setTitle(appSpeed, "")
        ac.drawBorder(appSpeed, 0)
        ac.setBackgroundOpacity(appSpeed, 0.0)
        ac.setIconPosition(appSpeed, -10000, -10000)
        ac.addRenderCallback(appSpeed, drawSpeedGL)

        lblSpeed = ac.addLabel(appSpeed, "0 KM/H")
        ac.setPosition(lblSpeed, int(round(70 * scale)), int(round(42 * scale)))
        ac.setFontSize(lblSpeed, int(round(28 * scale)))
        ac.setFontAlignment(lblSpeed, "center")

        lblSpeedLabel = ac.addLabel(appSpeed, "Speedometer")
        ac.setPosition(lblSpeedLabel, int(round(70 * scale)), int(round(105 * scale)))
        ac.setFontSize(lblSpeedLabel, int(round(8 * scale)))
        ac.setFontAlignment(lblSpeedLabel, "center")
        ac.setFontColor(lblSpeedLabel, 0.4, 0.4, 0.4, 1.0)

        lblGear = ac.addLabel(appSpeed, "G1")
        ac.setPosition(lblGear, int(round(215 * scale)), int(round(34 * scale)))
        ac.setFontSize(lblGear, int(round(24 * scale)))
        ac.setFontAlignment(lblGear, "center")

        lblGForce = ac.addLabel(appSpeed, "0.00 / 0.00")
        ac.setPosition(lblGForce, int(round(215 * scale)), int(round(75 * scale)))
        ac.setFontSize(lblGForce, int(round(9 * scale)))
        ac.setFontAlignment(lblGForce, "center")

        lblGearLabel = ac.addLabel(appSpeed, "G-Force / Gear")
        ac.setPosition(lblGearLabel, int(round(215 * scale)), int(round(105 * scale)))
        ac.setFontSize(lblGearLabel, int(round(8 * scale)))
        ac.setFontAlignment(lblGearLabel, "center")
        ac.setFontColor(lblGearLabel, 0.4, 0.4, 0.4, 1.0)

        # ---------------------------------------------
        # 4. APP: PEDAL INPUTS (162px x 70px)
        # ---------------------------------------------
        appPedals = ac.newApp("AlaschgariHUD - Pedals")
        ac.setSize(appPedals, int(round(162 * scale)), int(round(70 * scale)))
        ac.setTitle(appPedals, "")
        ac.drawBorder(appPedals, 0)
        ac.setBackgroundOpacity(appPedals, 0.0)
        ac.setIconPosition(appPedals, -10000, -10000)
        ac.addRenderCallback(appPedals, drawPedalsGL)

        lblPedalClutch = ac.addLabel(appPedals, "Clutch")
        ac.setPosition(lblPedalClutch, int(round(8 * scale)), int(round(5 * scale)))
        ac.setFontSize(lblPedalClutch, int(round(8 * scale)))

        lblPedalBrake = ac.addLabel(appPedals, "Brake")
        ac.setPosition(lblPedalBrake, int(round(8 * scale)), int(round(23 * scale)))
        ac.setFontSize(lblPedalBrake, int(round(8 * scale)))

        lblPedalThrottle = ac.addLabel(appPedals, "Throt")
        ac.setPosition(lblPedalThrottle, int(round(8 * scale)), int(round(41 * scale)))
        ac.setFontSize(lblPedalThrottle, int(round(8 * scale)))

        lblPedalClutchVal = ac.addLabel(appPedals, "0%")
        ac.setPosition(lblPedalClutchVal, int(round(154 * scale)), int(round(5 * scale)))
        ac.setFontSize(lblPedalClutchVal, int(round(8 * scale)))
        ac.setFontAlignment(lblPedalClutchVal, "right")

        lblPedalBrakeVal = ac.addLabel(appPedals, "0%")
        ac.setPosition(lblPedalBrakeVal, int(round(154 * scale)), int(round(23 * scale)))
        ac.setFontSize(lblPedalBrakeVal, int(round(8 * scale)))
        ac.setFontAlignment(lblPedalBrakeVal, "right")

        lblPedalThrottleVal = ac.addLabel(appPedals, "0%")
        ac.setPosition(lblPedalThrottleVal, int(round(154 * scale)), int(round(41 * scale)))
        ac.setFontSize(lblPedalThrottleVal, int(round(8 * scale)))
        ac.setFontAlignment(lblPedalThrottleVal, "right")

        # ---------------------------------------------
        # 5. APP: KERS & TIRE WEAR (162px x 45px)
        # ---------------------------------------------
        appKers = ac.newApp("AlaschgariHUD - KERS & Wear")
        ac.setSize(appKers, int(round(162 * scale)), int(round(45 * scale)))
        ac.setTitle(appKers, "")
        ac.drawBorder(appKers, 0)
        ac.setBackgroundOpacity(appKers, 0.0)
        ac.setIconPosition(appKers, -10000, -10000)
        ac.addRenderCallback(appKers, drawKersGL)

        lblKersName = ac.addLabel(appKers, "KERS")
        ac.setPosition(lblKersName, int(round(12 * scale)), int(round(16 * scale)))
        ac.setFontSize(lblKersName, int(round(9 * scale)))

        lblWearName = ac.addLabel(appKers, "WEAR")
        ac.setPosition(lblWearName, int(round(90 * scale)), int(round(16 * scale)))
        ac.setFontSize(lblWearName, int(round(9 * scale)))

        # ---------------------------------------------
        # 5b. APP: LAPS & TIMES (162px x 70px)
        # ---------------------------------------------
        appTimes = ac.newApp("AlaschgariHUD - Laps & Times")
        ac.setSize(appTimes, int(round(162 * scale)), int(round(70 * scale)))
        ac.setTitle(appTimes, "")
        ac.drawBorder(appTimes, 0)
        ac.setBackgroundOpacity(appTimes, 0.0)
        ac.setIconPosition(appTimes, -10000, -10000)
        ac.addRenderCallback(appTimes, drawTimesGL)

        lblTimesCurrent = ac.addLabel(appTimes, "--:--.-")
        ac.setPosition(lblTimesCurrent, int(round(81 * scale)), int(round(22 * scale)))
        ac.setFontSize(lblTimesCurrent, int(round(15 * scale)))
        ac.setFontAlignment(lblTimesCurrent, "center")

        lblTimesBest = ac.addLabel(appTimes, "Best: --:--.---")
        ac.setPosition(lblTimesBest, int(round(8 * scale)), int(round(5 * scale)))
        ac.setFontSize(lblTimesBest, int(round(8 * scale)))

        lblTimesLast = ac.addLabel(appTimes, "Last: --:--.---")
        ac.setPosition(lblTimesLast, int(round(154 * scale)), int(round(5 * scale)))
        ac.setFontSize(lblTimesLast, int(round(8 * scale)))
        ac.setFontAlignment(lblTimesLast, "right")

        lblTimesLaps = ac.addLabel(appTimes, "Lap 1")
        ac.setPosition(lblTimesLaps, int(round(81 * scale)), int(round(50 * scale)))
        ac.setFontSize(lblTimesLaps, int(round(8 * scale)))
        ac.setFontAlignment(lblTimesLaps, "center")

        # ---------------------------------------------
        # 5c. APP: FUEL CALCULATOR (162px x 70px)
        # ---------------------------------------------
        appFuel = ac.newApp("AlaschgariHUD - Fuel Calculator")
        ac.setSize(appFuel, int(round(162 * scale)), int(round(70 * scale)))
        ac.setTitle(appFuel, "")
        ac.drawBorder(appFuel, 0)
        ac.setBackgroundOpacity(appFuel, 0.0)
        ac.setIconPosition(appFuel, -10000, -10000)
        ac.addRenderCallback(appFuel, drawFuelGL)

        lblFuelCurrent = ac.addLabel(appFuel, "0.0 L")
        ac.setPosition(lblFuelCurrent, int(round(81 * scale)), int(round(22 * scale)))
        ac.setFontSize(lblFuelCurrent, int(round(14 * scale)))
        ac.setFontAlignment(lblFuelCurrent, "center")

        lblFuelCons = ac.addLabel(appFuel, "Cons: -- L")
        ac.setPosition(lblFuelCons, int(round(8 * scale)), int(round(5 * scale)))
        ac.setFontSize(lblFuelCons, int(round(8 * scale)))

        lblFuelEst = ac.addLabel(appFuel, "Est: -- Laps")
        ac.setPosition(lblFuelEst, int(round(154 * scale)), int(round(5 * scale)))
        ac.setFontSize(lblFuelEst, int(round(8 * scale)))
        ac.setFontAlignment(lblFuelEst, "right")

        lblFuelTemps = ac.addLabel(appFuel, "T: 0 C | A: 0 C")
        ac.setPosition(lblFuelTemps, int(round(81 * scale)), int(round(50 * scale)))
        ac.setFontSize(lblFuelTemps, int(round(8 * scale)))
        ac.setFontAlignment(lblFuelTemps, "center")

        # Setup main debug label in tires app window as anchor
        lblDebugError = ac.addLabel(appTires, "")
        ac.setPosition(lblDebugError, int(round(10 * scale)), int(round(115 * scale)))
        ac.setFontSize(lblDebugError, int(round(8 * scale)))
        ac.setFontColor(lblDebugError, 1.0, 0.2, 0.2, 1.0)

        # ---------------------------------------------
        # 6. APP: HUD IN-GAME CONFIG WINDOW (180px height for multi options)
        # ---------------------------------------------
        appSettings = ac.newApp("AlaschgariHUD - Config")
        ac.setSize(appSettings, 250, 180)
        ac.setTitle(appSettings, "AlaschgariHUD Options")
        
        # 1. Scale
        lblSliderName = ac.addLabel(appSettings, "HUD Scale: {0:.0f}%".format(scale * 100))
        ac.setPosition(lblSliderName, 10, 30)
        ac.setFontSize(lblSliderName, 9)

        sliderScale = ac.addSpinner(appSettings, "")
        ac.setPosition(sliderScale, 120, 28)
        ac.setSize(sliderScale, 110, 18)
        ac.setRange(sliderScale, 50, 150)
        ac.setStep(sliderScale, 5)
        ac.setValue(sliderScale, int(scale * 100))
        last_spinner_value = int(scale * 100)

        # 2. Opacity
        lblOpacityName = ac.addLabel(appSettings, "HUD Opacity: {0}%".format(opacity_pct))
        ac.setPosition(lblOpacityName, 10, 65)
        ac.setFontSize(lblOpacityName, 9)

        sliderOpacity = ac.addSpinner(appSettings, "")
        ac.setPosition(sliderOpacity, 120, 63)
        ac.setSize(sliderOpacity, 110, 18)
        ac.setRange(sliderOpacity, 10, 100)
        ac.setStep(sliderOpacity, 10)
        ac.setValue(sliderOpacity, opacity_pct)
        last_opacity_value = opacity_pct

        # 3. BG Color theme
        lblBgColorName = ac.addLabel(appSettings, "BG Color (0-3): {0}".format(bg_color_idx))
        ac.setPosition(lblBgColorName, 10, 100)
        ac.setFontSize(lblBgColorName, 9)

        sliderBgColor = ac.addSpinner(appSettings, "")
        ac.setPosition(sliderBgColor, 120, 98)
        ac.setSize(sliderBgColor, 110, 18)
        ac.setRange(sliderBgColor, 0, 3)
        ac.setStep(sliderBgColor, 1)
        ac.setValue(sliderBgColor, bg_color_idx)
        last_bg_color_value = bg_color_idx

        # 4. Text Color theme
        lblTextColorName = ac.addLabel(appSettings, "Text Color (0-4): {0}".format(text_color_idx))
        ac.setPosition(lblTextColorName, 10, 135)
        ac.setFontSize(lblTextColorName, 9)

        sliderTextColor = ac.addSpinner(appSettings, "")
        ac.setPosition(sliderTextColor, 120, 133)
        ac.setSize(sliderTextColor, 110, 18)
        ac.setRange(sliderTextColor, 0, 4)
        ac.setStep(sliderTextColor, 1)
        ac.setValue(sliderTextColor, text_color_idx)
        last_text_color_value = text_color_idx

        # Apply starting custom text colors
        applyTextColors()

        # Check for early startup errors and display them
        try:
            path = os.path.join(os.path.dirname(__file__), 'error.log')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    err_lines = [l.strip() for l in f if l.strip()]
                    if err_lines:
                        ac.setText(lblDebugError, "START ERR: " + err_lines[-1][:65])
        except:
            pass

        # Max RPM default check from shared memory
        if simInfo is not None:
            maxRpm = simInfo.static.maxRpm
        if maxRpm <= 0:
            maxRpm = 8000

        return appName
    except Exception as e:
        log_error("acMain crash:\n" + traceback.format_exc())
        return appName

def getTireColor(temp):
    try:
        t = float(temp)
    except:
        t = 0.0
    if t < 70.0:
        return [0.1, 0.4, 0.8, 0.9] # Cold blue
    elif t > 95.0:
        return [1.0, 0.2, 0.2, 0.9] # Hot red
    else:
        return [0.0, 1.0, 0.4, 0.9] # Optimal green

# -------------------------------------------------------------
# DRAW ROUNDED RECTANGLE UTILITY
# -------------------------------------------------------------
def drawRoundedRect(x, y, w, h, r, color):
    ac.glColor4f(color[0], color[1], color[2], color[3])
    # Central body
    ac.glQuad(x + r, y, w - 2*r, h)
    # Left flank
    ac.glQuad(x, y + r, r, h - 2*r)
    # Right flank
    ac.glQuad(x + w - r, y + r, r, h - 2*r)
    
    # Corner circles approximation using vertical segments
    for dx in range(r):
        dy = int(round(math.sqrt(r*r - dx*dx)))
        # Top-Left
        ac.glQuad(x + r - dx - 1, y + r - dy, 1, dy)
        # Top-Right
        ac.glQuad(x + w - r + dx, y + r - dy, 1, dy)
        # Bottom-Left
        ac.glQuad(x + r - dx - 1, y + h - r, 1, dy)
        # Bottom-Right
        ac.glQuad(x + w - r + dx, y + h - r, 1, dy)

# Get current background color matching theme & opacity index
def getBGColor():
    c = BG_COLORS[bg_color_idx]
    op = opacity_pct / 100.0
    return [c[0], c[1], c[2], op]

# -------------------------------------------------------------
# INDIVIDUAL OPENGL RENDER CALLBACKS FOR FLOATING WINDOWS
# -------------------------------------------------------------

def drawShiftGL(deltaT):
    global rpms, maxRpm, scale, show_rpm
    if not show_rpm or maxRpm <= 0:
        return

    try:
        pct = float(rpms) / float(maxRpm)
        if pct > 1.0: pct = 1.0
        if pct < 0.0: pct = 0.0

        total_segments = 24
        segment_gap = 2
        bar_w = 480 * scale
        segment_width = (bar_w - (segment_gap * scale * (total_segments - 1))) / total_segments
        active_segments = int(round(pct * total_segments))

        is_flashing = (pct >= 0.92) and (int(rpms * 0.1) % 2 == 0)

        for i in range(total_segments):
            x = i * (segment_width + (segment_gap * scale))
            col = [0.15, 0.15, 0.15, 0.8]

            if is_flashing:
                col = [1.0, 0.2, 0.2, 1.0] if (int(rpms * 0.1) % 2 == 0) else [0.0, 0.94, 1.0, 1.0]
            elif i < active_segments:
                if i < total_segments * 0.6:
                    col = [0.0, 1.0, 0.4, 0.9]
                elif i < total_segments * 0.85:
                    col = [1.0, 1.0, 0.0, 0.9]
                else:
                    col = [1.0, 0.2, 0.2, 0.9]

            ac.glColor4f(col[0], col[1], col[2], col[3])
            ac.glQuad(int(x), 0, int(segment_width), int(12 * scale))
    except Exception as e:
        log_error("drawShiftGL failed:\n" + traceback.format_exc())

def drawTiresGL(deltaT):
    global tireTemps, scale, show_chassis, show_tire_bars, brakeTemps
    try:
        # Rounded Panel Background (Height remains 112px inside 125px window)
        col_bg = getBGColor()
        drawRoundedRect(0, 0, int(round(310 * scale)), int(round(112 * scale)), int(round(6 * scale)), col_bg)

        # Chassis
        if show_chassis:
            ac.glColor4f(1.0, 1.0, 1.0, 0.12)
            # Outline
            ac.glQuad(int(round(110 * scale)), int(round(10 * scale)), int(round(60 * scale)), int(round(90 * scale)))
            # Axles
            ac.glQuad(int(round(95 * scale)), int(round(30 * scale)), int(round(90 * scale)), int(round(1.5 * scale)))
            ac.glQuad(int(round(95 * scale)), int(round(80 * scale)), int(round(90 * scale)), int(round(1.5 * scale)))

        # Tires (FL, FR, RL, RR)
        # FL
        col = getTireColor(tireTemps[0])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(80 * scale)), int(round(10 * scale)), int(round(14 * scale)), int(round(26 * scale)))

        # FR
        col = getTireColor(tireTemps[1])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(168 * scale)), int(round(10 * scale)), int(round(14 * scale)), int(round(26 * scale)))

        # RL
        col = getTireColor(tireTemps[2])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(80 * scale)), int(round(60 * scale)), int(round(14 * scale)), int(round(26 * scale)))

        # RR
        col = getTireColor(tireTemps[3])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(168 * scale)), int(round(60 * scale)), int(round(14 * scale)), int(round(26 * scale)))

        if show_tire_bars:
            # FL Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(80 * scale)), int(round(39 * scale)), int(round(20 * scale)), int(round(4 * scale)))
            col = getTireColor(tireTemps[0])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[0]) - 40.0) / 80.0))
            ac.glQuad(int(round(80 * scale)), int(round(39 * scale)), int(round(20 * pct * scale)), int(round(4 * scale)))

            # FR Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(168 * scale)), int(round(39 * scale)), int(round(20 * scale)), int(round(4 * scale)))
            col = getTireColor(tireTemps[1])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[1]) - 40.0) / 80.0))
            ac.glQuad(int(round(168 * scale)), int(round(39 * scale)), int(round(20 * pct * scale)), int(round(4 * scale)))

            # RL Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(80 * scale)), int(round(89 * scale)), int(round(20 * scale)), int(round(4 * scale)))
            col = getTireColor(tireTemps[2])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[2]) - 40.0) / 80.0))
            ac.glQuad(int(round(80 * scale)), int(round(89 * scale)), int(round(20 * pct * scale)), int(round(4 * scale)))

            # RR Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(168 * scale)), int(round(89 * scale)), int(round(20 * scale)), int(round(4 * scale)))
            col = getTireColor(tireTemps[3])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[3]) - 40.0) / 80.0))
            ac.glQuad(int(round(168 * scale)), int(round(89 * scale)), int(round(20 * pct * scale)), int(round(4 * scale)))

        # Brake Indicator Bars
        ac.glColor4f(1.0, 0.2, 0.2, 0.8)
        bf_pct = max(0.0, min(1.0, float(brakeTemps[0]) / 800.0))
        ac.glQuad(int(round(265 * scale)), int(round(20 * scale)), int(round(30 * bf_pct * scale)), int(round(5 * scale)))
        br_pct = max(0.0, min(1.0, float(brakeTemps[2]) / 800.0))
        ac.glQuad(int(round(265 * scale)), int(round(70 * scale)), int(round(30 * br_pct * scale)), int(round(5 * scale)))
    except Exception as e:
        log_error("drawTiresGL failed:\n" + traceback.format_exc())

def drawSpeedGL(deltaT):
    global scale, speed, text_color_idx
    try:
        col_bg = getBGColor()
        # Speedometer Box with rounded corners (Height 112px inside 125px window)
        drawRoundedRect(0, 0, int(round(140 * scale)), int(round(112 * scale)), int(round(6 * scale)), col_bg)
        # Gear / G-Force Box with rounded corners (Height 112px inside 125px window)
        drawRoundedRect(int(round(150 * scale)), 0, int(round(140 * scale)), int(round(112 * scale)), int(round(6 * scale)), col_bg)

        # Draw Speedometer Circular Gauge Track (0 to 300 KM/H)
        ac.glColor4f(0.15, 0.15, 0.15, 0.8)
        cx, cy = 70.0, 48.0
        r = 46.0
        for deg in range(-220, 40, 3):
            rad = math.radians(deg)
            px = int(round((cx + r * math.cos(rad)) * scale))
            py = int(round((cy + r * math.sin(rad)) * scale))
            ac.glQuad(px - int(round(2 * scale)), py - int(round(2 * scale)), int(round(4 * scale)), int(round(4 * scale)))

        # Draw Active Speedometer Gauge Arc (Colored)
        c = TEXT_COLORS[text_color_idx]
        ac.glColor4f(c[0], c[1], c[2], 0.9)
        speed_pct = max(0.0, min(1.0, float(speed) / 300.0))
        active_deg = int(round(speed_pct * 260.0))
        
        for deg in range(-220, -220 + active_deg, 3):
            rad = math.radians(deg)
            px = int(round((cx + r * math.cos(rad)) * scale))
            py = int(round((cy + r * math.sin(rad)) * scale))
            ac.glQuad(px - int(round(2 * scale)), py - int(round(2 * scale)), int(round(4 * scale)), int(round(4 * scale)))
            
    except Exception as e:
        log_error("drawSpeedGL failed:\n" + traceback.format_exc())

def drawPedalsGL(deltaT):
    global scale, clutchInput, brakeInput, throttleInput
    try:
        col_bg = getBGColor()
        drawRoundedRect(0, 0, int(round(162 * scale)), int(round(70 * scale)), int(round(6 * scale)), col_bg)

        # Fills backgrounds
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(round(50 * scale)), int(round(7 * scale)), int(round(65 * scale)), int(round(8 * scale)))
        ac.glQuad(int(round(50 * scale)), int(round(25 * scale)), int(round(65 * scale)), int(round(8 * scale)))
        ac.glQuad(int(round(50 * scale)), int(round(43 * scale)), int(round(65 * scale)), int(round(8 * scale)))

        # Fill: Clutch
        ac.glColor4f(0.0, 0.5, 1.0, 0.9)
        ac.glQuad(int(round(50 * scale)), int(round(7 * scale)), int(round(65 * clutchInput * scale)), int(round(8 * scale)))

        # Fill: Brake
        ac.glColor4f(1.0, 0.2, 0.2, 0.9)
        ac.glQuad(int(round(50 * scale)), int(round(25 * scale)), int(round(65 * brakeInput * scale)), int(round(8 * scale)))

        # Fill: Throttle
        ac.glColor4f(0.0, 1.0, 0.4, 0.9)
        ac.glQuad(int(round(50 * scale)), int(round(43 * scale)), int(round(65 * throttleInput * scale)), int(round(8 * scale)))
    except Exception as e:
        log_error("drawPedalsGL failed:\n" + traceback.format_exc())

def drawKersGL(deltaT):
    global scale, kersCharge, tyreWear
    try:
        col_bg = getBGColor()
        # Kers Box
        drawRoundedRect(0, 0, int(round(76 * scale)), int(round(45 * scale)), int(round(4 * scale)), col_bg)
        # Wear Box
        drawRoundedRect(int(round(86 * scale)), 0, int(round(76 * scale)), int(round(45 * scale)), int(round(4 * scale)), col_bg)

        # Kers Inner Bar
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(round(56 * scale)), int(round(4 * scale)), int(round(8 * scale)), int(round(37 * scale)))
        ac.glColor4f(0.0, 0.94, 1.0, 0.9)
        ac.glQuad(int(round(56 * scale)), int(round(4 * scale + (37 * (1.0 - kersCharge)) * scale)), int(round(8 * scale)), int(round(37 * kersCharge * scale)))

        # Wear Inner Bar
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(round(142 * scale)), int(round(4 * scale)), int(round(8 * scale)), int(round(37 * scale)))
        ac.glColor4f(0.6, 0.6, 0.6, 0.9)
        wear_left = max(0.0, min(1.0, 1.0 - tyreWear))
        ac.glQuad(int(round(142 * scale)), int(round(4 * scale + (37 * (1.0 - wear_left)) * scale)), int(round(8 * scale)), int(round(37 * wear_left * scale)))
    except Exception as e:
        log_error("drawKersGL failed:\n" + traceback.format_exc())

def drawTimesGL(deltaT):
    global scale
    try:
        col_bg = getBGColor()
        drawRoundedRect(0, 0, int(round(162 * scale)), int(round(70 * scale)), int(round(6 * scale)), col_bg)
    except Exception as e:
        log_error("drawTimesGL failed:\n" + traceback.format_exc())

def drawFuelGL(deltaT):
    global scale
    try:
        col_bg = getBGColor()
        drawRoundedRect(0, 0, int(round(162 * scale)), int(round(70 * scale)), int(round(6 * scale)), col_bg)
    except Exception as e:
        log_error("drawFuelGL failed:\n" + traceback.format_exc())

def acUpdate(deltaT):
    global gear, speed, rpms, fuel, tireTemps, tirePressures, maxRpm, scale
    global lblGear, lblSpeed, lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR, lblGForce
    global clutchInput, brakeInput, throttleInput, kersCharge, tyreWear, brakeTemps, gForceLat, gForceLon
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    global last_lap_completed, fuel_at_lap_start, fuel_consumptions, fuel_per_lap_avg
    global last_spinner_value, sliderScale, lblSliderName
    global last_opacity_value, sliderOpacity, lblOpacityName, opacity_pct
    global last_bg_color_value, sliderBgColor, lblBgColorName, bg_color_idx
    global last_text_color_value, sliderTextColor, lblTextColorName, text_color_idx

    # 0. Check in-game Scale, Opacity, and Colors Spinners
    try:
        # Scale
        if sliderScale != 0:
            current_val = int(round(ac.getValue(sliderScale)))
            if current_val != last_spinner_value:
                last_spinner_value = current_val
                updateScale(current_val / 100.0)
                ac.setText(lblSliderName, "HUD Scale: {0}%".format(current_val))
                saveConfig()
        
        # Opacity
        if sliderOpacity != 0:
            current_op = int(round(ac.getValue(sliderOpacity)))
            if current_op != last_opacity_value:
                last_opacity_value = current_op
                opacity_pct = current_op
                ac.setText(lblOpacityName, "HUD Opacity: {0}%".format(current_op))
                saveConfig()

        # BG Color Theme
        if sliderBgColor != 0:
            current_bg = int(round(ac.getValue(sliderBgColor)))
            if current_bg != last_bg_color_value:
                last_bg_color_value = current_bg
                bg_color_idx = current_bg
                ac.setText(lblBgColorName, "BG Color (0-3): {0}".format(current_bg))
                saveConfig()

        # Text Color Theme
        if sliderTextColor != 0:
            current_txt = int(round(ac.getValue(sliderTextColor)))
            if current_txt != last_text_color_value:
                last_text_color_value = current_txt
                text_color_idx = current_txt
                ac.setText(lblTextColorName, "Text Color (0-4): {0}".format(current_txt))
                applyTextColors()
                saveConfig()
    except Exception as e:
        log_error("Spinner update failed:\n" + traceback.format_exc())

    # 1. Update Gear
    try:
        g = ac.getCarState(0, acsys.CS.Gear)
        if g == 0:
            gear = "R"
        elif g == 1:
            gear = "N"
        else:
            gear = "G" + str(g - 1)
        ac.setText(lblGear, gear)
    except Exception as e:
        log_error("Gear update failed:\n" + traceback.format_exc())

    # 2. Update Speed
    try:
        speed = ac.getCarState(0, acsys.CS.SpeedKMH)
        ac.setText(lblSpeed, "{0:.0f} KM/H".format(speed))
    except Exception as e:
        log_error("Speed update failed:\n" + traceback.format_exc())

    # 3. Update Pedals & G-Forces
    try:
        clutchInput = ac.getCarState(0, acsys.CS.Clutch)
        brakeInput = ac.getCarState(0, acsys.CS.Brake)
        throttleInput = ac.getCarState(0, acsys.CS.Gas)

        ac.setText(lblPedalClutchVal, "{0:.0f}%".format(clutchInput * 100.0))
        ac.setText(lblPedalBrakeVal, "{0:.0f}%".format(brakeInput * 100.0))
        ac.setText(lblPedalThrottleVal, "{0:.0f}%".format(throttleInput * 100.0))

        g_vec = ac.getCarState(0, acsys.CS.AccG)
        if isinstance(g_vec, list) or isinstance(g_vec, tuple):
            gForceLat = g_vec[0]
            gForceLon = g_vec[2]
        ac.setText(lblGForce, "{0:.2f} / {1:.2f}".format(gForceLat, gForceLon))
    except Exception as e:
        log_error("Pedal/GForce update failed:\n" + traceback.format_exc())

    # 4. Update Shared Memory (SM) values
    if simInfo is not None:
        # RPM
        try:
            rpms = simInfo.physics.rpms
            maxRpm = simInfo.static.maxRpm
        except Exception as e:
            log_error("RPM SM update failed:\n" + traceback.format_exc())

        # KERS & Wear
        try:
            kersCharge = simInfo.physics.kersCharge
            wear_sum = 0.0
            for i in range(4):
                wear_sum += simInfo.physics.tyreWear[i]
            tyreWear = wear_sum / 4.0
        except Exception as e:
            log_error("Kers/Wear SM update failed:\n" + traceback.format_exc())

        # Tires (Temps & Pressure Deltas from Ideal 28.0 PSI)
        try:
            for i in range(4):
                tireTemps[i] = simInfo.physics.tyreCoreTemperature[i]
                tirePressures[i] = simInfo.physics.wheelsPressure[i]
            
            ac.setText(lblPressFL, "{0:.0f}\n{1:+.1f}".format(tireTemps[0], tirePressures[0] - 28.0))
            ac.setText(lblPressFR, "{0:.0f}\n{1:+.1f}".format(tireTemps[1], tirePressures[1] - 28.0))
            ac.setText(lblPressRL, "{0:.0f}\n{1:+.1f}".format(tireTemps[2], tirePressures[2] - 28.0))
            ac.setText(lblPressRR, "{0:.0f}\n{1:+.1f}".format(tireTemps[3], tirePressures[3] - 28.0))
        except Exception as e:
            log_error("Tires SM update failed:\n" + traceback.format_exc())

        # Brakes
        try:
            for i in range(4):
                brakeTemps[i] = simInfo.physics.brakeTemp[i]
            ac.setText(lblBrakeF, "{0:.0f}".format(brakeTemps[0]))
            ac.setText(lblBrakeR, "{0:.0f}".format(brakeTemps[2]))
        except Exception as e:
            log_error("Brakes SM update failed:\n" + traceback.format_exc())

    # 5. Update Laps & Times
    try:
        current_lap = ac.getCarState(0, acsys.CS.LapTime)
        last_lap = ac.getCarState(0, acsys.CS.LastLap)
        best_lap = ac.getCarState(0, acsys.CS.BestLap)
        
        laps = 0
        if simInfo is not None:
            laps = simInfo.graphics.completedLaps

        ac.setText(lblTimesCurrent, formatTimeShort(current_lap))
        ac.setText(lblTimesBest, "Best: " + formatTime(best_lap))
        ac.setText(lblTimesLast, "Last: " + formatTime(last_lap))
        ac.setText(lblTimesLaps, "Lap {}".format(laps + 1))
    except Exception as e:
        log_error("Times update failed:\n" + traceback.format_exc())

    # 6. Update Fuel & Environment temperatures
    if simInfo is not None:
        try:
            laps = simInfo.graphics.completedLaps
            current_fuel = simInfo.physics.fuel
            
            # Fuel consumption math
            if fuel_at_lap_start < 0.0:
                fuel_at_lap_start = current_fuel
                last_lap_completed = laps
            
            if laps > last_lap_completed:
                consumed = fuel_at_lap_start - current_fuel
                if 0.1 < consumed < 20.0:
                    fuel_consumptions.append(consumed)
                    if len(fuel_consumptions) > 5:
                        fuel_consumptions.pop(0)
                    fuel_per_lap_avg = sum(fuel_consumptions) / len(fuel_consumptions)
                fuel_at_lap_start = current_fuel
                last_lap_completed = laps

            # Show Fuel Current
            ac.setText(lblFuelCurrent, "{0:.1f} L".format(current_fuel))

            # Show Fuel Consumption
            if fuel_per_lap_avg > 0.0:
                ac.setText(lblFuelCons, "Cons: {0:.2f} L/L".format(fuel_per_lap_avg))
                ac.setText(lblFuelEst, "Est: {0:.1f} Laps".format(current_fuel / fuel_per_lap_avg))
            else:
                ac.setText(lblFuelCons, "Cons: -- L/L")
                ac.setText(lblFuelEst, "Est: -- Laps")

            # Show Air & Road Temps
            air_t = simInfo.physics.airTemp
            road_t = simInfo.physics.roadTemp
            ac.setText(lblFuelTemps, "Track: {0:.0f} C | Air: {1:.0f} C".format(road_t, air_t))

        except Exception as e:
            log_error("Fuel/Temps update failed:\n" + traceback.format_exc())
