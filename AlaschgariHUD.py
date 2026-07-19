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

# Global Debug controls
appDebug = 0
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
            ac.setFontColor(lblDebugError, 1.0, 0.2, 0.2, 1.0) # Red for error
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

# Individual scale factors with defaults (in float)
scale_shift = 1.0
scale_tires = 1.0
scale_speed = 1.0
scale_gear = 1.0
scale_pedals = 1.0
scale_kers = 1.0
scale_times = 1.0
scale_fuel = 1.0
scale_perf = 1.0
scale_damage = 1.0
scale_track = 1.0
scale_debug = 1.0

# General Settings
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
appGear = 0
appPedals = 0
appKers = 0
appTimes = 0
appFuel = 0
appPerf = 0
appDamage = 0
appTrack = 0
appSettings = 0

# UI Controls per app window
# Tires App
lblPressFL = 0
lblPressFR = 0
lblPressRL = 0
lblPressRR = 0
lblBrakeF = 0
lblBrakeR = 0
imgChassis = 0

# Speed App
lblSpeed = 0
lblSpeedLabel = 0

# Gear App
lblGear = 0
lblGearLabel = 0
lblGForce = 0

# Pedals App
lblPedalClutchVal = 0
lblPedalBrakeVal = 0
lblPedalThrottleVal = 0
imgPedalClutch = 0
imgPedalBrake = 0
imgPedalThrottle = 0

# KERS & Wear App
imgKers = 0
imgWear = 0

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

# Performance / Delta App
imgPerf = 0
lblPerfDelta = 0
lblPerfTurbo = 0
lblPerfDRS = 0

# Damage App
imgDamage = 0
lblDamageEngine = 0
lblDamageAero = 0
lblDamageTrans = 0

# Track App
imgTrack = 0
lblTrackGrip = 0
lblTrackWind = 0

# Settings App controls
lblOpacityName = 0
sliderOpacity = 0
lblBgColorName = 0
sliderBgColor = 0
lblTextColorName = 0
sliderTextColor = 0

# Spinners for individual scale factors
sliderScaleShift = 0
sliderScaleTires = 0
sliderScaleSpeed = 0
sliderScaleGear = 0
sliderScalePedals = 0
sliderScaleKers = 0
sliderScaleTimes = 0
sliderScaleFuel = 0
sliderScalePerf = 0
sliderScaleDamage = 0
sliderScaleTrack = 0
sliderScaleDebug = 0

# Plus buttons on each widget
btnScaleShift = 0
btnScaleTires = 0
btnScaleSpeed = 0
btnScaleGear = 0
btnScalePedals = 0
btnScaleKers = 0
btnScaleTimes = 0
btnScaleFuel = 0
btnScalePerf = 0
btnScaleDamage = 0
btnScaleTrack = 0
btnScaleDebug = 0

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

# Performance telemetry
perfDelta = 0.0
turboBoost = 0.0
drsAvailable = False
drsEnabled = False

# Damage telemetry
dmgEngine = 0.0
dmgAero = 0.0
dmgTrans = 0.0

# Track weather telemetry
surfaceGrip = 1.0
windSpeed = 0.0
windDir = 0.0

# Fuel Calculator State
last_lap_completed = -1
fuel_at_lap_start = -1.0
fuel_consumptions = []
fuel_per_lap_avg = 0.0

# Settings tracker variables
last_opacity_value = 65.0
last_bg_color_value = 0.0
last_text_color_value = 0.0

# Track last scale values to avoid redundant updates
last_scale_shift = 100.0
last_scale_tires = 100.0
last_scale_speed = 100.0
last_scale_gear = 100.0
last_scale_pedals = 100.0
last_scale_kers = 100.0
last_scale_times = 100.0
last_scale_fuel = 100.0
last_scale_perf = 100.0
last_scale_damage = 100.0
last_scale_track = 100.0
last_scale_debug = 100.0

def getConfigPath():
    return os.path.join(os.path.dirname(__file__), 'config.ini')

def loadConfig():
    global scale_shift, scale_tires, scale_speed, scale_gear, scale_pedals, scale_kers, scale_times, scale_fuel, scale_perf, scale_damage, scale_track, scale_debug
    global show_rpm, show_chassis, show_tire_bars, bg_color_idx, opacity_pct, text_color_idx
    path = getConfigPath()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k == 'scale_shift': scale_shift = float(v) / 100.0
                        elif k == 'scale_tires': scale_tires = float(v) / 100.0
                        elif k == 'scale_speed': scale_speed = float(v) / 100.0
                        elif k == 'scale_gear': scale_gear = float(v) / 100.0
                        elif k == 'scale_pedals': scale_pedals = float(v) / 100.0
                        elif k == 'scale_kers': scale_kers = float(v) / 100.0
                        elif k == 'scale_times': scale_times = float(v) / 100.0
                        elif k == 'scale_fuel': scale_fuel = float(v) / 100.0
                        elif k == 'scale_perf': scale_perf = float(v) / 100.0
                        elif k == 'scale_damage': scale_damage = float(v) / 100.0
                        elif k == 'scale_track': scale_track = float(v) / 100.0
                        elif k == 'scale_debug': scale_debug = float(v) / 100.0
                        elif k == 'show_rpm': show_rpm = (v.lower() == 'true')
                        elif k == 'show_chassis': show_chassis = (v.lower() == 'true')
                        elif k == 'show_tire_bars': show_tire_bars = (v.lower() == 'true')
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
            f.write("scale_shift = " + str(int(scale_shift * 100)) + "\n")
            f.write("scale_tires = " + str(int(scale_tires * 100)) + "\n")
            f.write("scale_speed = " + str(int(scale_speed * 100)) + "\n")
            f.write("scale_gear = " + str(int(scale_gear * 100)) + "\n")
            f.write("scale_pedals = " + str(int(scale_pedals * 100)) + "\n")
            f.write("scale_kers = " + str(int(scale_kers * 100)) + "\n")
            f.write("scale_times = " + str(int(scale_times * 100)) + "\n")
            f.write("scale_fuel = " + str(int(scale_fuel * 100)) + "\n")
            f.write("scale_perf = " + str(int(scale_perf * 100)) + "\n")
            f.write("scale_damage = " + str(int(scale_damage * 100)) + "\n")
            f.write("scale_track = " + str(int(scale_track * 100)) + "\n")
            f.write("scale_debug = " + str(int(scale_debug * 100)) + "\n")
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
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    global lblPerfDelta, lblPerfTurbo, lblPerfDRS
    global lblDamageEngine, lblDamageAero, lblDamageTrans
    global lblTrackGrip, lblTrackWind, lblGear
    
    try:
        c = TEXT_COLORS[text_color_idx]
        labels = [
            lblSpeed, lblGForce, lblPressFL, lblPressFR, lblPressRL, lblPressRR,
            lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal,
            lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps,
            lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps,
            lblPerfDelta, lblPerfTurbo, lblPerfDRS,
            lblDamageEngine, lblDamageAero, lblDamageTrans,
            lblTrackGrip, lblTrackWind, lblGear
        ]
        for lbl in labels:
            if lbl != 0:
                ac.setFontColor(lbl, c[0], c[1], c[2], c[3])
    except Exception as e:
        log_error("applyTextColors failed:\n" + traceback.format_exc())

def updateWindowsBackground():
    global appTires, appSpeed, appGear, appPedals, appKers, appTimes, appFuel, appPerf, appDamage, appTrack, appDebug
    global bg_color_idx, opacity_pct
    try:
        c = BG_COLORS[bg_color_idx]
        op = opacity_pct / 100.0
        for app in [appTires, appSpeed, appGear, appPedals, appKers, appTimes, appFuel, appPerf, appDamage, appTrack, appDebug]:
            if app != 0:
                ac.setBackgroundColor(app, c[0], c[1], c[2])
                ac.setBackgroundOpacity(app, op)
    except Exception as e:
        log_error("updateWindowsBackground failed:\n" + traceback.format_exc())

# Individual Widget Scaling Hooks
def updateScaleShift(s):
    global scale_shift, btnScaleShift
    scale_shift = s
    ac.setSize(appShift, int(round(480 * scale_shift)), int(round(20 * scale_shift)))
    if btnScaleShift != 0:
        ac.setPosition(btnScaleShift, int(round(462 * scale_shift)), 0)
        ac.setSize(btnScaleShift, int(round(18 * scale_shift)), int(round(18 * scale_shift)))

def updateScaleTires(s):
    global scale_tires, btnScaleTires
    global appTires, lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR, imgChassis
    scale_tires = s
    ac.setSize(appTires, int(round(310 * scale_tires)), int(round(125 * scale_tires)))
    ac.setPosition(lblPressFL, int(round(15 * scale_tires)), int(round(22 * scale_tires)))
    ac.setFontSize(lblPressFL, int(round(24 * scale_tires)))
    ac.setPosition(lblPressRL, int(round(15 * scale_tires)), int(round(72 * scale_tires)))
    ac.setFontSize(lblPressRL, int(round(24 * scale_tires)))
    ac.setPosition(lblPressFR, int(round(212 * scale_tires)), int(round(22 * scale_tires)))
    ac.setFontSize(lblPressFR, int(round(24 * scale_tires)))
    ac.setPosition(lblPressRR, int(round(212 * scale_tires)), int(round(72 * scale_tires)))
    ac.setFontSize(lblPressRR, int(round(24 * scale_tires)))
    ac.setPosition(lblBrakeF, int(round(265 * scale_tires)), int(round(22 * scale_tires)))
    ac.setFontSize(lblBrakeF, int(round(24 * scale_tires)))
    ac.setPosition(lblBrakeR, int(round(265 * scale_tires)), int(round(72 * scale_tires)))
    ac.setFontSize(lblBrakeR, int(round(24 * scale_tires)))
    if imgChassis != 0:
        ac.setPosition(imgChassis, int(round(110 * scale_tires)), int(round(10 * scale_tires)))
        ac.setSize(imgChassis, int(round(90 * scale_tires)), int(round(90 * scale_tires)))
    if btnScaleTires != 0:
        ac.setPosition(btnScaleTires, int(round(292 * scale_tires)), 0)
        ac.setSize(btnScaleTires, int(round(18 * scale_tires)), int(round(18 * scale_tires)))

def updateScaleSpeed(s):
    global scale_speed, btnScaleSpeed
    global appSpeed, lblSpeed, lblSpeedLabel
    scale_speed = s
    ac.setSize(appSpeed, int(round(140 * scale_speed)), int(round(125 * scale_speed)))
    ac.setPosition(lblSpeed, int(round(70 * scale_speed)), int(round(42 * scale_speed)))
    ac.setFontSize(lblSpeed, int(round(24 * scale_speed)))
    ac.setPosition(lblSpeedLabel, int(round(70 * scale_speed)), int(round(105 * scale_speed)))
    ac.setFontSize(lblSpeedLabel, int(round(24 * scale_speed)))
    if btnScaleSpeed != 0:
        ac.setPosition(btnScaleSpeed, int(round(122 * scale_speed)), 0)
        ac.setSize(btnScaleSpeed, int(round(18 * scale_speed)), int(round(18 * scale_speed)))

def updateScaleGear(s):
    global scale_gear, btnScaleGear
    global appGear, lblGear, lblGForce, lblGearLabel
    scale_gear = s
    ac.setSize(appGear, int(round(140 * scale_gear)), int(round(125 * scale_gear)))
    ac.setPosition(lblGear, int(round(70 * scale_gear)), int(round(34 * scale_gear)))
    ac.setFontSize(lblGear, int(round(24 * scale_gear)))
    ac.setPosition(lblGForce, int(round(70 * scale_gear)), int(round(75 * scale_gear)))
    ac.setFontSize(lblGForce, int(round(24 * scale_gear)))
    ac.setPosition(lblGearLabel, int(round(70 * scale_gear)), int(round(105 * scale_gear)))
    ac.setFontSize(lblGearLabel, int(round(24 * scale_gear)))
    if btnScaleGear != 0:
        ac.setPosition(btnScaleGear, int(round(122 * scale_gear)), 0)
        ac.setSize(btnScaleGear, int(round(18 * scale_gear)), int(round(18 * scale_gear)))

def updateScalePedals(s):
    global scale_pedals, btnScalePedals
    global appPedals, imgPedalClutch, imgPedalBrake, imgPedalThrottle, lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    scale_pedals = s
    ac.setSize(appPedals, int(round(162 * scale_pedals)), int(round(70 * scale_pedals)))
    if imgPedalClutch != 0:
        ac.setPosition(imgPedalClutch, int(round(12 * scale_pedals)), int(round(4 * scale_pedals)))
        ac.setSize(imgPedalClutch, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))
    if imgPedalBrake != 0:
        ac.setPosition(imgPedalBrake, int(round(12 * scale_pedals)), int(round(25 * scale_pedals)))
        ac.setSize(imgPedalBrake, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))
    if imgPedalThrottle != 0:
        ac.setPosition(imgPedalThrottle, int(round(12 * scale_pedals)), int(round(46 * scale_pedals)))
        ac.setSize(imgPedalThrottle, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))

    ac.setPosition(lblPedalClutchVal, int(round(154 * scale_pedals)), int(round(5 * scale_pedals)))
    ac.setFontSize(lblPedalClutchVal, int(round(24 * scale_pedals)))
    ac.setPosition(lblPedalBrakeVal, int(round(154 * scale_pedals)), int(round(23 * scale_pedals)))
    ac.setFontSize(lblPedalBrakeVal, int(round(24 * scale_pedals)))
    ac.setPosition(lblPedalThrottleVal, int(round(154 * scale_pedals)), int(round(41 * scale_pedals)))
    ac.setFontSize(lblPedalThrottleVal, int(round(24 * scale_pedals)))
    if btnScalePedals != 0:
        ac.setPosition(btnScalePedals, int(round(144 * scale_pedals)), 0)
        ac.setSize(btnScalePedals, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))

def updateScaleKers(s):
    global scale_kers, btnScaleKers
    global appKers, imgKers, imgWear
    scale_kers = s
    ac.setSize(appKers, int(round(162 * scale_kers)), int(round(45 * scale_kers)))
    if imgKers != 0:
        ac.setPosition(imgKers, int(round(12 * scale_kers)), int(round(10 * scale_kers)))
        ac.setSize(imgKers, int(round(24 * scale_kers)), int(round(24 * scale_kers)))
    if imgWear != 0:
        ac.setPosition(imgWear, int(round(94 * scale_kers)), int(round(10 * scale_kers)))
        ac.setSize(imgWear, int(round(24 * scale_kers)), int(round(24 * scale_kers)))
    if btnScaleKers != 0:
        ac.setPosition(btnScaleKers, int(round(144 * scale_kers)), 0)
        ac.setSize(btnScaleKers, int(round(18 * scale_kers)), int(round(18 * scale_kers)))

def updateScaleTimes(s):
    global scale_times, btnScaleTimes
    global appTimes, lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    scale_times = s
    ac.setSize(appTimes, int(round(162 * scale_times)), int(round(70 * scale_times)))
    ac.setPosition(lblTimesCurrent, int(round(81 * scale_times)), int(round(22 * scale_times)))
    ac.setFontSize(lblTimesCurrent, int(round(24 * scale_times)))
    ac.setPosition(lblTimesBest, int(round(8 * scale_times)), int(round(5 * scale_times)))
    ac.setFontSize(lblTimesBest, int(round(24 * scale_times)))
    ac.setPosition(lblTimesLast, int(round(154 * scale_times)), int(round(5 * scale_times)))
    ac.setFontSize(lblTimesLast, int(round(24 * scale_times)))
    ac.setPosition(lblTimesLaps, int(round(81 * scale_times)), int(round(50 * scale_times)))
    ac.setFontSize(lblTimesLaps, int(round(24 * scale_times)))
    if btnScaleTimes != 0:
        ac.setPosition(btnScaleTimes, int(round(144 * scale_times)), 0)
        ac.setSize(btnScaleTimes, int(round(18 * scale_times)), int(round(18 * scale_times)))

def updateScaleFuel(s):
    global scale_fuel, btnScaleFuel
    global appFuel, lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    scale_fuel = s
    ac.setSize(appFuel, int(round(162 * scale_fuel)), int(round(70 * scale_fuel)))
    ac.setPosition(lblFuelCurrent, int(round(81 * scale_fuel)), int(round(22 * scale_fuel)))
    ac.setFontSize(lblFuelCurrent, int(round(24 * scale_fuel)))
    ac.setPosition(lblFuelCons, int(round(8 * scale_fuel)), int(round(5 * scale_fuel)))
    ac.setFontSize(lblFuelCons, int(round(24 * scale_fuel)))
    ac.setPosition(lblFuelEst, int(round(154 * scale_fuel)), int(round(5 * scale_fuel)))
    ac.setFontSize(lblFuelEst, int(round(24 * scale_fuel)))
    ac.setPosition(lblFuelTemps, int(round(81 * scale_fuel)), int(round(50 * scale_fuel)))
    ac.setFontSize(lblFuelTemps, int(round(24 * scale_fuel)))
    if btnScaleFuel != 0:
        ac.setPosition(btnScaleFuel, int(round(144 * scale_fuel)), 0)
        ac.setSize(btnScaleFuel, int(round(18 * scale_fuel)), int(round(18 * scale_fuel)))

def updateScalePerf(s):
    global scale_perf, btnScalePerf
    global appPerf, imgPerf, lblPerfDelta, lblPerfTurbo, lblPerfDRS
    scale_perf = s
    ac.setSize(appPerf, int(round(162 * scale_perf)), int(round(70 * scale_perf)))
    if imgPerf != 0:
        ac.setPosition(imgPerf, int(round(12 * scale_perf)), int(round(23 * scale_perf)))
        ac.setSize(imgPerf, int(round(24 * scale_perf)), int(round(24 * scale_perf)))
    ac.setPosition(lblPerfDelta, int(round(102 * scale_perf)), int(round(22 * scale_perf)))
    ac.setFontSize(lblPerfDelta, int(round(24 * scale_perf)))
    ac.setPosition(lblPerfTurbo, int(round(8 * scale_perf)), int(round(5 * scale_perf)))
    ac.setFontSize(lblPerfTurbo, int(round(24 * scale_perf)))
    ac.setPosition(lblPerfDRS, int(round(154 * scale_perf)), int(round(5 * scale_perf)))
    ac.setFontSize(lblPerfDRS, int(round(24 * scale_perf)))
    if btnScalePerf != 0:
        ac.setPosition(btnScalePerf, int(round(144 * scale_perf)), 0)
        ac.setSize(btnScalePerf, int(round(18 * scale_perf)), int(round(18 * scale_perf)))

def updateScaleDamage(s):
    global scale_damage, btnScaleDamage
    global appDamage, imgDamage, lblDamageEngine, lblDamageAero, lblDamageTrans
    scale_damage = s
    ac.setSize(appDamage, int(round(162 * scale_damage)), int(round(70 * scale_damage)))
    if imgDamage != 0:
        ac.setPosition(imgDamage, int(round(12 * scale_damage)), int(round(23 * scale_damage)))
        ac.setSize(imgDamage, int(round(24 * scale_damage)), int(round(24 * scale_damage)))
    ac.setPosition(lblDamageEngine, int(round(102 * scale_damage)), int(round(22 * scale_damage)))
    ac.setFontSize(lblDamageEngine, int(round(24 * scale_damage)))
    ac.setPosition(lblDamageAero, int(round(8 * scale_damage)), int(round(5 * scale_damage)))
    ac.setFontSize(lblDamageAero, int(round(24 * scale_damage)))
    ac.setPosition(lblDamageTrans, int(round(154 * scale_damage)), int(round(5 * scale_damage)))
    ac.setFontSize(lblDamageTrans, int(round(24 * scale_damage)))
    if btnScaleDamage != 0:
        ac.setPosition(btnScaleDamage, int(round(144 * scale_damage)), 0)
        ac.setSize(btnScaleDamage, int(round(18 * scale_damage)), int(round(18 * scale_damage)))

def updateScaleTrack(s):
    global scale_track, btnScaleTrack
    global appTrack, imgTrack, lblTrackGrip, lblTrackWind
    scale_track = s
    ac.setSize(appTrack, int(round(162 * scale_track)), int(round(70 * scale_track)))
    if imgTrack != 0:
        ac.setPosition(imgTrack, int(round(12 * scale_track)), int(round(23 * scale_track)))
        ac.setSize(imgTrack, int(round(24 * scale_track)), int(round(24 * scale_track)))
    ac.setPosition(lblTrackGrip, int(round(102 * scale_track)), int(round(22 * scale_track)))
    ac.setFontSize(lblTrackGrip, int(round(24 * scale_track)))
    ac.setPosition(lblTrackWind, int(round(8 * scale_track)), int(round(5 * scale_track)))
    ac.setFontSize(lblTrackWind, int(round(24 * scale_track)))
    if btnScaleTrack != 0:
        ac.setPosition(btnScaleTrack, int(round(144 * scale_track)), 0)
        ac.setSize(btnScaleTrack, int(round(18 * scale_track)), int(round(18 * scale_track)))

def updateScaleDebug(s):
    global scale_debug, btnScaleDebug
    global appDebug, lblDebugError
    scale_debug = s
    ac.setSize(appDebug, int(round(310 * scale_debug)), int(round(40 * scale_debug)))
    ac.setPosition(lblDebugError, int(round(10 * scale_debug)), int(round(12 * scale_debug)))
    ac.setFontSize(lblDebugError, int(round(24 * scale_debug)))
    if btnScaleDebug != 0:
        ac.setPosition(btnScaleDebug, int(round(292 * scale_debug)), 0)
        ac.setSize(btnScaleDebug, int(round(18 * scale_debug)), int(round(18 * scale_debug)))

# Click callbacks for Plus buttons
def onScaleShiftClick(x, y):
    global scale_shift, sliderScaleShift
    scale_shift = round(scale_shift + 0.1, 1)
    if scale_shift > 1.5: scale_shift = 0.5
    updateScaleShift(scale_shift)
    if sliderScaleShift != 0: ac.setValue(sliderScaleShift, int(scale_shift * 100))
    saveConfig()

def onScaleTiresClick(x, y):
    global scale_tires, sliderScaleTires
    scale_tires = round(scale_tires + 0.1, 1)
    if scale_tires > 1.5: scale_tires = 0.5
    updateScaleTires(scale_tires)
    if sliderScaleTires != 0: ac.setValue(sliderScaleTires, int(scale_tires * 100))
    saveConfig()

def onScaleSpeedClick(x, y):
    global scale_speed, sliderScaleSpeed
    scale_speed = round(scale_speed + 0.1, 1)
    if scale_speed > 1.5: scale_speed = 0.5
    updateScaleSpeed(scale_speed)
    if sliderScaleSpeed != 0: ac.setValue(sliderScaleSpeed, int(scale_speed * 100))
    saveConfig()

def onScaleGearClick(x, y):
    global scale_gear, sliderScaleGear
    scale_gear = round(scale_gear + 0.1, 1)
    if scale_gear > 1.5: scale_gear = 0.5
    updateScaleGear(scale_gear)
    if sliderScaleGear != 0: ac.setValue(sliderScaleGear, int(scale_gear * 100))
    saveConfig()

def onScalePedalsClick(x, y):
    global scale_pedals, sliderScalePedals
    scale_pedals = round(scale_pedals + 0.1, 1)
    if scale_pedals > 1.5: scale_pedals = 0.5
    updateScalePedals(scale_pedals)
    if sliderScalePedals != 0: ac.setValue(sliderScalePedals, int(scale_pedals * 100))
    saveConfig()

def onScaleKersClick(x, y):
    global scale_kers, sliderScaleKers
    scale_kers = round(scale_kers + 0.1, 1)
    if scale_kers > 1.5: scale_kers = 0.5
    updateScaleKers(scale_kers)
    if sliderScaleKers != 0: ac.setValue(sliderScaleKers, int(scale_kers * 100))
    saveConfig()

def onScaleTimesClick(x, y):
    global scale_times, sliderScaleTimes
    scale_times = round(scale_times + 0.1, 1)
    if scale_times > 1.5: scale_times = 0.5
    updateScaleTimes(scale_times)
    if sliderScaleTimes != 0: ac.setValue(sliderScaleTimes, int(scale_times * 100))
    saveConfig()

def onScaleFuelClick(x, y):
    global scale_fuel, sliderScaleFuel
    scale_fuel = round(scale_fuel + 0.1, 1)
    if scale_fuel > 1.5: scale_fuel = 0.5
    updateScaleFuel(scale_fuel)
    if sliderScaleFuel != 0: ac.setValue(sliderScaleFuel, int(scale_fuel * 100))
    saveConfig()

def onScalePerfClick(x, y):
    global scale_perf, sliderScalePerf
    scale_perf = round(scale_perf + 0.1, 1)
    if scale_perf > 1.5: scale_perf = 0.5
    updateScalePerf(scale_perf)
    if sliderScalePerf != 0: ac.setValue(sliderScalePerf, int(scale_perf * 100))
    saveConfig()

def onScaleDamageClick(x, y):
    global scale_damage, sliderScaleDamage
    scale_damage = round(scale_damage + 0.1, 1)
    if scale_damage > 1.5: scale_damage = 0.5
    updateScaleDamage(scale_damage)
    if sliderScaleDamage != 0: ac.setValue(sliderScaleDamage, int(scale_damage * 100))
    saveConfig()

def onScaleTrackClick(x, y):
    global scale_track, sliderScaleTrack
    scale_track = round(scale_track + 0.1, 1)
    if scale_track > 1.5: scale_track = 0.5
    updateScaleTrack(scale_track)
    if sliderScaleTrack != 0: ac.setValue(sliderScaleTrack, int(scale_track * 100))
    saveConfig()

def onScaleDebugClick(x, y):
    global scale_debug, sliderScaleDebug
    scale_debug = round(scale_debug + 0.1, 1)
    if scale_debug > 1.5: scale_debug = 0.5
    updateScaleDebug(scale_debug)
    if sliderScaleDebug != 0: ac.setValue(sliderScaleDebug, int(scale_debug * 100))
    saveConfig()

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

def createBoldLabel(app, text):
    lbl = ac.addLabel(app, text)
    ac.setFontBold(lbl, 1)
    return lbl

def acMain(ac_version):
    global scale_shift, scale_tires, scale_speed, scale_gear, scale_pedals, scale_kers, scale_times, scale_fuel, scale_perf, scale_damage, scale_track, scale_debug
    global lblDebugError, bg_color_idx, opacity_pct, text_color_idx
    global appShift, appTires, appSpeed, appGear, appPedals, appKers, appTimes, appFuel, appPerf, appDamage, appTrack, appDebug, appSettings
    global lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR, imgChassis
    global lblSpeed, lblSpeedLabel, lblGear, lblGearLabel, lblGForce
    global imgPedalClutch, imgPedalBrake, imgPedalThrottle, lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global imgKers, imgWear
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    global imgPerf, lblPerfDelta, lblPerfTurbo, lblPerfDRS
    global imgDamage, lblDamageEngine, lblDamageAero, lblDamageTrans
    global imgTrack, lblTrackGrip, lblTrackWind
    global lblOpacityName, sliderOpacity, lblBgColorName, sliderBgColor, lblTextColorName, sliderTextColor
    global sliderScaleShift, sliderScaleTires, sliderScaleSpeed, sliderScaleGear, sliderScalePedals, sliderScaleKers, sliderScaleTimes, sliderScaleFuel, sliderScalePerf, sliderScaleDamage, sliderScaleTrack, sliderScaleDebug
    global btnScaleShift, btnScaleTires, btnScaleSpeed, btnScaleGear, btnScalePedals, btnScaleKers, btnScaleTimes, btnScaleFuel, btnScalePerf, btnScaleDamage, btnScaleTrack, btnScaleDebug
    global last_opacity_value, last_bg_color_value, last_text_color_value
    global last_scale_shift, last_scale_tires, last_scale_speed, last_scale_gear, last_scale_pedals, last_scale_kers, last_scale_times, last_scale_fuel, last_scale_perf, last_scale_damage, last_scale_track, last_scale_debug

    try:
        loadConfig()

        # ---------------------------------------------
        # 1. APP: SHIFT LIGHT BAR (480px x 20px)
        # ---------------------------------------------
        appShift = ac.newApp("AlaschgariHUD - Shift Lights")
        ac.setSize(appShift, int(round(480 * scale_shift)), int(round(20 * scale_shift)))
        ac.setTitle(appShift, "")
        ac.drawBorder(appShift, 0)
        ac.setBackgroundOpacity(appShift, 0.0)
        ac.setIconPosition(appShift, -10000, -10000)
        ac.addRenderCallback(appShift, drawShiftGL)

        btnScaleShift = ac.addButton(appShift, "+")
        ac.setText(btnScaleShift, "+")
        ac.addOnClickedListener(btnScaleShift, onScaleShiftClick)

        # ---------------------------------------------
        # 2. APP: TIRES & BRAKES STATUS (310px x 125px)
        # ---------------------------------------------
        appTires = ac.newApp("AlaschgariHUD - Tires & Brakes")
        ac.setSize(appTires, int(round(310 * scale_tires)), int(round(125 * scale_tires)))
        ac.setTitle(appTires, "")
        ac.drawBorder(appTires, 0)
        ac.setIconPosition(appTires, -10000, -10000)
        ac.addRenderCallback(appTires, drawTiresGL)

        btnScaleTires = ac.addButton(appTires, "+")
        ac.setText(btnScaleTires, "+")
        ac.addOnClickedListener(btnScaleTires, onScaleTiresClick)

        # Labels
        lblPressFL = createBoldLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressFL, int(round(15 * scale_tires)), int(round(22 * scale_tires)))
        ac.setFontSize(lblPressFL, int(round(24 * scale_tires)))

        lblPressRL = createBoldLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressRL, int(round(15 * scale_tires)), int(round(72 * scale_tires)))
        ac.setFontSize(lblPressRL, int(round(24 * scale_tires)))

        lblPressFR = createBoldLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressFR, int(round(212 * scale_tires)), int(round(22 * scale_tires)))
        ac.setFontSize(lblPressFR, int(round(24 * scale_tires)))
        ac.setFontAlignment(lblPressFR, "right")

        lblPressRR = createBoldLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressRR, int(round(212 * scale_tires)), int(round(72 * scale_tires)))
        ac.setFontSize(lblPressRR, int(round(24 * scale_tires)))
        ac.setFontAlignment(lblPressRR, "right")

        lblBrakeF = createBoldLabel(appTires, "0")
        ac.setPosition(lblBrakeF, int(round(265 * scale_tires)), int(round(22 * scale_tires)))
        ac.setFontSize(lblBrakeF, int(round(24 * scale_tires)))
        ac.setFontColor(lblBrakeF, 1.0, 0.2, 0.2, 1.0)

        lblBrakeR = createBoldLabel(appTires, "0")
        ac.setPosition(lblBrakeR, int(round(265 * scale_tires)), int(round(72 * scale_tires)))
        ac.setFontSize(lblBrakeR, int(round(24 * scale_tires)))
        ac.setFontColor(lblBrakeR, 1.0, 0.2, 0.2, 1.0)

        # Car Chassis Vector Overlay
        imgChassis = ac.addLabel(appTires, "")
        ac.setBackgroundTexture(imgChassis, "apps/python/AlaschgariHUD/images/chassis_vector.png")
        ac.setPosition(imgChassis, int(round(110 * scale_tires)), int(round(10 * scale_tires)))
        ac.setSize(imgChassis, int(round(90 * scale_tires)), int(round(90 * scale_tires)))

        # ---------------------------------------------
        # 3. APP: SPEEDOMETER (140px x 125px)
        # ---------------------------------------------
        appSpeed = ac.newApp("AlaschgariHUD - Speedometer")
        ac.setSize(appSpeed, int(round(140 * scale_speed)), int(round(125 * scale_speed)))
        ac.setTitle(appSpeed, "")
        ac.drawBorder(appSpeed, 0)
        ac.setIconPosition(appSpeed, -10000, -10000)
        ac.addRenderCallback(appSpeed, drawSpeedGL)

        btnScaleSpeed = ac.addButton(appSpeed, "+")
        ac.setText(btnScaleSpeed, "+")
        ac.addOnClickedListener(btnScaleSpeed, onScaleSpeedClick)

        lblSpeed = createBoldLabel(appSpeed, "0 KM/H")
        ac.setPosition(lblSpeed, int(round(70 * scale_speed)), int(round(42 * scale_speed)))
        ac.setFontSize(lblSpeed, int(round(24 * scale_speed)))
        ac.setFontAlignment(lblSpeed, "center")

        lblSpeedLabel = createBoldLabel(appSpeed, "Speedometer")
        ac.setPosition(lblSpeedLabel, int(round(70 * scale_speed)), int(round(105 * scale_speed)))
        ac.setFontSize(lblSpeedLabel, int(round(24 * scale_speed)))
        ac.setFontAlignment(lblSpeedLabel, "center")
        ac.setFontColor(lblSpeedLabel, 0.4, 0.4, 0.4, 1.0)

        # ---------------------------------------------
        # 3b. APP: GEAR & G-FORCE (140px x 125px)
        # ---------------------------------------------
        appGear = ac.newApp("AlaschgariHUD - Gear & G-Force")
        ac.setSize(appGear, int(round(140 * scale_gear)), int(round(125 * scale_gear)))
        ac.setTitle(appGear, "")
        ac.drawBorder(appGear, 0)
        ac.setIconPosition(appGear, -10000, -10000)

        btnScaleGear = ac.addButton(appGear, "+")
        ac.setText(btnScaleGear, "+")
        ac.addOnClickedListener(btnScaleGear, onScaleGearClick)

        lblGear = createBoldLabel(appGear, "G1")
        ac.setPosition(lblGear, int(round(70 * scale_gear)), int(round(34 * scale_gear)))
        ac.setFontSize(lblGear, int(round(24 * scale_gear)))
        ac.setFontAlignment(lblGear, "center")

        lblGForce = createBoldLabel(appGear, "0.00 / 0.00")
        ac.setPosition(lblGForce, int(round(70 * scale_gear)), int(round(75 * scale_gear)))
        ac.setFontSize(lblGForce, int(round(24 * scale_gear)))
        ac.setFontAlignment(lblGForce, "center")

        lblGearLabel = createBoldLabel(appGear, "G-Force / Gear")
        ac.setPosition(lblGearLabel, int(round(70 * scale_gear)), int(round(105 * scale_gear)))
        ac.setFontSize(lblGearLabel, int(round(24 * scale_gear)))
        ac.setFontAlignment(lblGearLabel, "center")
        ac.setFontColor(lblGearLabel, 0.4, 0.4, 0.4, 1.0)

        # ---------------------------------------------
        # 4. APP: PEDAL INPUTS (162px x 70px)
        # ---------------------------------------------
        appPedals = ac.newApp("AlaschgariHUD - Pedals")
        ac.setSize(appPedals, int(round(162 * scale_pedals)), int(round(70 * scale_pedals)))
        ac.setTitle(appPedals, "")
        ac.drawBorder(appPedals, 0)
        ac.setIconPosition(appPedals, -10000, -10000)
        ac.addRenderCallback(appPedals, drawPedalsGL)

        btnScalePedals = ac.addButton(appPedals, "+")
        ac.setText(btnScalePedals, "+")
        ac.addOnClickedListener(btnScalePedals, onScalePedalsClick)

        # Pedal Custom Vector Icons (Standardized size to 18x18)
        imgPedalClutch = ac.addLabel(appPedals, "")
        ac.setBackgroundTexture(imgPedalClutch, "apps/python/AlaschgariHUD/images/pedal_brake.png")
        ac.setPosition(imgPedalClutch, int(round(12 * scale_pedals)), int(round(4 * scale_pedals)))
        ac.setSize(imgPedalClutch, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))

        imgPedalBrake = ac.addLabel(appPedals, "")
        ac.setBackgroundTexture(imgPedalBrake, "apps/python/AlaschgariHUD/images/pedal_brake.png")
        ac.setPosition(imgPedalBrake, int(round(12 * scale_pedals)), int(round(25 * scale_pedals)))
        ac.setSize(imgPedalBrake, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))

        imgPedalThrottle = ac.addLabel(appPedals, "")
        ac.setBackgroundTexture(imgPedalThrottle, "apps/python/AlaschgariHUD/images/pedal_throttle.png")
        ac.setPosition(imgPedalThrottle, int(round(12 * scale_pedals)), int(round(46 * scale_pedals)))
        ac.setSize(imgPedalThrottle, int(round(18 * scale_pedals)), int(round(18 * scale_pedals)))

        lblPedalClutchVal = createBoldLabel(appPedals, "0%")
        ac.setPosition(lblPedalClutchVal, int(round(154 * scale_pedals)), int(round(5 * scale_pedals)))
        ac.setFontSize(lblPedalClutchVal, int(round(24 * scale_pedals)))
        ac.setFontAlignment(lblPedalClutchVal, "right")

        lblPedalBrakeVal = createBoldLabel(appPedals, "0%")
        ac.setPosition(lblPedalBrakeVal, int(round(154 * scale_pedals)), int(round(23 * scale_pedals)))
        ac.setFontSize(lblPedalBrakeVal, int(round(24 * scale_pedals)))
        ac.setFontAlignment(lblPedalBrakeVal, "right")

        lblPedalThrottleVal = createBoldLabel(appPedals, "0%")
        ac.setPosition(lblPedalThrottleVal, int(round(154 * scale_pedals)), int(round(41 * scale_pedals)))
        ac.setFontSize(lblPedalThrottleVal, int(round(24 * scale_pedals)))
        ac.setFontAlignment(lblPedalThrottleVal, "right")

        # ---------------------------------------------
        # 5. APP: KERS & TIRE WEAR (162px x 45px)
        # ---------------------------------------------
        appKers = ac.newApp("AlaschgariHUD - KERS & Wear")
        ac.setSize(appKers, int(round(162 * scale_kers)), int(round(45 * scale_kers)))
        ac.setTitle(appKers, "")
        ac.drawBorder(appKers, 0)
        ac.setIconPosition(appKers, -10000, -10000)
        ac.addRenderCallback(appKers, drawKersGL)

        btnScaleKers = ac.addButton(appKers, "+")
        ac.setText(btnScaleKers, "+")
        ac.addOnClickedListener(btnScaleKers, onScaleKersClick)

        # KERS & Wear Vector Icons (Standardized size to 24x24)
        imgKers = ac.addLabel(appKers, "")
        ac.setBackgroundTexture(imgKers, "apps/python/AlaschgariHUD/images/kers_icon.png")
        ac.setPosition(imgKers, int(round(12 * scale_kers)), int(round(10 * scale_kers)))
        ac.setSize(imgKers, int(round(24 * scale_kers)), int(round(24 * scale_kers)))

        imgWear = ac.addLabel(appKers, "")
        ac.setBackgroundTexture(imgWear, "apps/python/AlaschgariHUD/images/wear_icon.png")
        ac.setPosition(imgWear, int(round(94 * scale_kers)), int(round(10 * scale_kers)))
        ac.setSize(imgWear, int(round(24 * scale_kers)), int(round(24 * scale_kers)))

        # ---------------------------------------------
        # 5b. APP: LAPS & TIMES (162px x 70px)
        # ---------------------------------------------
        appTimes = ac.newApp("AlaschgariHUD - Laps & Times")
        ac.setSize(appTimes, int(round(162 * scale_times)), int(round(70 * scale_times)))
        ac.setTitle(appTimes, "")
        ac.drawBorder(appTimes, 0)
        ac.setIconPosition(appTimes, -10000, -10000)
        ac.addRenderCallback(appTimes, drawTimesGL)

        btnScaleTimes = ac.addButton(appTimes, "+")
        ac.setText(btnScaleTimes, "+")
        ac.addOnClickedListener(btnScaleTimes, onScaleTimesClick)

        lblTimesCurrent = createBoldLabel(appTimes, "--:--.-")
        ac.setPosition(lblTimesCurrent, int(round(81 * scale_times)), int(round(22 * scale_times)))
        ac.setFontSize(lblTimesCurrent, int(round(24 * scale_times)))
        ac.setFontAlignment(lblTimesCurrent, "center")

        lblTimesBest = createBoldLabel(appTimes, "Best: --:--.---")
        ac.setPosition(lblTimesBest, int(round(8 * scale_times)), int(round(5 * scale_times)))
        ac.setFontSize(lblTimesBest, int(round(24 * scale_times)))

        lblTimesLast = createBoldLabel(appTimes, "Last: --:--.---")
        ac.setPosition(lblTimesLast, int(round(154 * scale_times)), int(round(5 * scale_times)))
        ac.setFontSize(lblTimesLast, int(round(24 * scale_times)))
        ac.setFontAlignment(lblTimesLast, "right")

        lblTimesLaps = createBoldLabel(appTimes, "Lap 1")
        ac.setPosition(lblTimesLaps, int(round(81 * scale_times)), int(round(50 * scale_times)))
        ac.setFontSize(lblTimesLaps, int(round(24 * scale_times)))
        ac.setFontAlignment(lblTimesLaps, "center")

        # ---------------------------------------------
        # 5c. APP: FUEL CALCULATOR (162px x 70px)
        # ---------------------------------------------
        appFuel = ac.newApp("AlaschgariHUD - Fuel Calculator")
        ac.setSize(appFuel, int(round(162 * scale_fuel)), int(round(70 * scale_fuel)))
        ac.setTitle(appFuel, "")
        ac.drawBorder(appFuel, 0)
        ac.setIconPosition(appFuel, -10000, -10000)
        ac.addRenderCallback(appFuel, drawFuelGL)

        btnScaleFuel = ac.addButton(appFuel, "+")
        ac.setText(btnScaleFuel, "+")
        ac.addOnClickedListener(btnScaleFuel, onScaleFuelClick)

        lblFuelCurrent = createBoldLabel(appFuel, "0.0 L")
        ac.setPosition(lblFuelCurrent, int(round(81 * scale_fuel)), int(round(22 * scale_fuel)))
        ac.setFontSize(lblFuelCurrent, int(round(24 * scale_fuel)))
        ac.setFontAlignment(lblFuelCurrent, "center")

        lblFuelCons = createBoldLabel(appFuel, "Cons: -- L")
        ac.setPosition(lblFuelCons, int(round(8 * scale_fuel)), int(round(5 * scale_fuel)))
        ac.setFontSize(lblFuelCons, int(round(24 * scale_fuel)))

        lblFuelEst = createBoldLabel(appFuel, "Est: -- Laps")
        ac.setPosition(lblFuelEst, int(round(154 * scale_fuel)), int(round(5 * scale_fuel)))
        ac.setFontSize(lblFuelEst, int(round(24 * scale_fuel)))
        ac.setFontAlignment(lblFuelEst, "right")

        lblFuelTemps = createBoldLabel(appFuel, "T: 0 C | A: 0 C")
        ac.setPosition(lblFuelTemps, int(round(81 * scale_fuel)), int(round(50 * scale_fuel)))
        ac.setFontSize(lblFuelTemps, int(round(24 * scale_fuel)))
        ac.setFontAlignment(lblFuelTemps, "center")

        # ---------------------------------------------
        # 5d. APP: PERFORMANCE & DELTA (162px x 70px)
        # ---------------------------------------------
        appPerf = ac.newApp("AlaschgariHUD - Delta & Performance")
        ac.setSize(appPerf, int(round(162 * scale_perf)), int(round(70 * scale_perf)))
        ac.setTitle(appPerf, "")
        ac.drawBorder(appPerf, 0)
        ac.setIconPosition(appPerf, -10000, -10000)

        btnScalePerf = ac.addButton(appPerf, "+")
        ac.setText(btnScalePerf, "+")
        ac.addOnClickedListener(btnScalePerf, onScalePerfClick)

        imgPerf = ac.addLabel(appPerf, "")
        ac.setBackgroundTexture(imgPerf, "apps/python/AlaschgariHUD/images/delta_icon.png")
        ac.setPosition(imgPerf, int(round(12 * scale_perf)), int(round(23 * scale_perf)))
        ac.setSize(imgPerf, int(round(24 * scale_perf)), int(round(24 * scale_perf)))

        lblPerfDelta = createBoldLabel(appPerf, "+0.00")
        ac.setPosition(lblPerfDelta, int(round(102 * scale_perf)), int(round(22 * scale_perf)))
        ac.setFontSize(lblPerfDelta, int(round(24 * scale_perf)))
        ac.setFontAlignment(lblPerfDelta, "center")

        lblPerfTurbo = createBoldLabel(appPerf, "Turbo: 0.0 bar")
        ac.setPosition(lblPerfTurbo, int(round(8 * scale_perf)), int(round(5 * scale_perf)))
        ac.setFontSize(lblPerfTurbo, int(round(24 * scale_perf)))

        lblPerfDRS = createBoldLabel(appPerf, "DRS: N/A")
        ac.setPosition(lblPerfDRS, int(round(154 * scale_perf)), int(round(5 * scale_perf)))
        ac.setFontSize(lblPerfDRS, int(round(24 * scale_perf)))
        ac.setFontAlignment(lblPerfDRS, "right")

        # ---------------------------------------------
        # 5e. APP: DAMAGE & ENGINE (162px x 70px)
        # ---------------------------------------------
        appDamage = ac.newApp("AlaschgariHUD - Damage & Engine")
        ac.setSize(appDamage, int(round(162 * scale_damage)), int(round(70 * scale_damage)))
        ac.setTitle(appDamage, "")
        ac.drawBorder(appDamage, 0)
        ac.setIconPosition(appDamage, -10000, -10000)

        btnScaleDamage = ac.addButton(appDamage, "+")
        ac.setText(btnScaleDamage, "+")
        ac.addOnClickedListener(btnScaleDamage, onScaleDamageClick)

        imgDamage = ac.addLabel(appDamage, "")
        ac.setBackgroundTexture(imgDamage, "apps/python/AlaschgariHUD/images/damage_icon.png")
        ac.setPosition(imgDamage, int(round(12 * scale_damage)), int(round(23 * scale_damage)))
        ac.setSize(imgDamage, int(round(24 * scale_damage)), int(round(24 * scale_damage)))

        lblDamageEngine = createBoldLabel(appDamage, "Eng: 100%")
        ac.setPosition(lblDamageEngine, int(round(102 * scale_damage)), int(round(22 * scale_damage)))
        ac.setFontSize(lblDamageEngine, int(round(24 * scale_damage)))
        ac.setFontAlignment(lblDamageEngine, "center")

        lblDamageAero = createBoldLabel(appDamage, "Aero: 0%")
        ac.setPosition(lblDamageAero, int(round(8 * scale_damage)), int(round(5 * scale_damage)))
        ac.setFontSize(lblDamageAero, int(round(24 * scale_damage)))

        lblDamageTrans = createBoldLabel(appDamage, "Gear: 100%")
        ac.setPosition(lblDamageTrans, int(round(154 * scale_damage)), int(round(5 * scale_damage)))
        ac.setFontSize(lblDamageTrans, int(round(24 * scale_damage)))
        ac.setFontAlignment(lblDamageTrans, "right")

        # ---------------------------------------------
        # 5f. APP: TRACK SURFACE & WIND (162px x 70px)
        # ---------------------------------------------
        appTrack = ac.newApp("AlaschgariHUD - Track & Wind")
        ac.setSize(appTrack, int(round(162 * scale_track)), int(round(70 * scale_track)))
        ac.setTitle(appTrack, "")
        ac.drawBorder(appTrack, 0)
        ac.setIconPosition(appTrack, -10000, -10000)

        btnScaleTrack = ac.addButton(appTrack, "+")
        ac.setText(btnScaleTrack, "+")
        ac.addOnClickedListener(btnScaleTrack, onScaleTrackClick)

        imgTrack = ac.addLabel(appTrack, "")
        ac.setBackgroundTexture(imgTrack, "apps/python/AlaschgariHUD/images/track_icon.png")
        ac.setPosition(imgTrack, int(round(12 * scale_track)), int(round(23 * scale_track)))
        ac.setSize(imgTrack, int(round(24 * scale_track)), int(round(24 * scale_track)))

        lblTrackGrip = createBoldLabel(appTrack, "Grip: 100%")
        ac.setPosition(lblTrackGrip, int(round(102 * scale_track)), int(round(22 * scale_track)))
        ac.setFontSize(lblTrackGrip, int(round(24 * scale_track)))
        ac.setFontAlignment(lblTrackGrip, "center")

        lblTrackWind = createBoldLabel(appTrack, "Wind: 0 km/h")
        ac.setPosition(lblTrackWind, int(round(8 * scale_track)), int(round(5 * scale_track)))
        ac.setFontSize(lblTrackWind, int(round(24 * scale_track)))

        # ---------------------------------------------
        # 5g. APP: ERROR LOG & DEBUG (310px x 40px)
        # ---------------------------------------------
        appDebug = ac.newApp("AlaschgariHUD - Debug Console")
        ac.setSize(appDebug, int(round(310 * scale_debug)), int(round(40 * scale_debug)))
        ac.setTitle(appDebug, "")
        ac.drawBorder(appDebug, 0)
        ac.setIconPosition(appDebug, -10000, -10000)

        btnScaleDebug = ac.addButton(appDebug, "+")
        ac.setText(btnScaleDebug, "+")
        ac.addOnClickedListener(btnScaleDebug, onScaleDebugClick)

        lblDebugError = createBoldLabel(appDebug, "System Health: OK")
        ac.setPosition(lblDebugError, int(round(10 * scale_debug)), int(round(12 * scale_debug)))
        ac.setFontSize(lblDebugError, int(round(24 * scale_debug)))
        ac.setFontColor(lblDebugError, 0.0, 1.0, 0.4, 1.0) # Toxic green for OK state

        # Apply starting backgrounds and opacities nativly
        updateWindowsBackground()

        # Apply starting sizes/positions for buttons
        updateScaleShift(scale_shift)
        updateScaleTires(scale_tires)
        updateScaleSpeed(scale_speed)
        updateScaleGear(scale_gear)
        updateScalePedals(scale_pedals)
        updateScaleKers(scale_kers)
        updateScaleTimes(scale_times)
        updateScaleFuel(scale_fuel)
        updateScalePerf(scale_perf)
        updateScaleDamage(scale_damage)
        updateScaleTrack(scale_track)
        updateScaleDebug(scale_debug)

        # ---------------------------------------------
        # 6. APP: HUD IN-GAME CONFIG WINDOW
        # ---------------------------------------------
        appSettings = ac.newApp("AlaschgariHUD")
        ac.setSize(appSettings, 320, 510)
        ac.setTitle(appSettings, "AlaschgariHUD Options")
        
        # Row layout generator
        def addConfigRow(name, minVal, maxVal, stepVal, startVal, y_pos):
            lbl = ac.addLabel(appSettings, name + ": {0}%".format(startVal))
            ac.setPosition(lbl, 10, y_pos)
            ac.setFontSize(lbl, 8)

            sp = ac.addSpinner(appSettings, "")
            ac.setPosition(sp, 190, y_pos - 2)
            ac.setSize(sp, 110, 16)
            ac.setRange(sp, minVal, maxVal)
            ac.setStep(sp, stepVal)
            ac.setValue(sp, startVal)
            return lbl, sp

        y = 30
        
        # General Styles (Config labels can stay standard sized for interface clarity)
        lblOpacityName, sliderOpacity = addConfigRow("HUD Opacity", 10, 100, 10, opacity_pct, y); y += 35
        lblBgColorName, sliderBgColor = addConfigRow("BG Theme (0-3)", 0, 3, 1, bg_color_idx, y); y += 35
        lblTextColorName, sliderTextColor = addConfigRow("Text Theme (0-4)", 0, 4, 1, text_color_idx, y); y += 35
        
        # Widget Scale settings
        _, sliderScaleShift = addConfigRow("Scale: Shift Lights", 50, 150, 5, int(scale_shift * 100), y); y += 30
        _, sliderScaleTires = addConfigRow("Scale: Tires Status", 50, 150, 5, int(scale_tires * 100), y); y += 30
        _, sliderScaleSpeed = addConfigRow("Scale: Speedometer", 50, 150, 5, int(scale_speed * 100), y); y += 30
        _, sliderScaleGear = addConfigRow("Scale: Gear Box", 50, 150, 5, int(scale_gear * 100), y); y += 30
        _, sliderScalePedals = addConfigRow("Scale: Pedals Input", 50, 150, 5, int(scale_pedals * 100), y); y += 30
        _, sliderScaleKers = addConfigRow("Scale: KERS & Wear", 50, 150, 5, int(scale_kers * 100), y); y += 30
        _, sliderScaleTimes = addConfigRow("Scale: Laps & Times", 50, 150, 5, int(scale_times * 100), y); y += 30
        _, sliderScaleFuel = addConfigRow("Scale: Fuel Calc", 50, 150, 5, int(scale_fuel * 100), y); y += 30
        _, sliderScalePerf = addConfigRow("Scale: Performance", 50, 150, 5, int(scale_perf * 100), y); y += 30
        _, sliderScaleDamage = addConfigRow("Scale: Damages", 50, 150, 5, int(scale_damage * 100), y); y += 30
        _, sliderScaleTrack = addConfigRow("Scale: Track Wind", 50, 150, 5, int(scale_track * 100), y); y += 30
        _, sliderScaleDebug = addConfigRow("Scale: Debug Console", 50, 150, 5, int(scale_debug * 100), y)

        # Apply starting custom text colors
        applyTextColors()

        # Check for early startup errors and display them
        try:
            path = os.path.join(os.path.dirname(__file__), 'error.log')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    err_lines = [l.strip() for l in f if l.strip()]
                    if err_lines:
                        ac.setFontColor(lblDebugError, 1.0, 0.2, 0.2, 1.0)
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
# INDIVIDUAL OPENGL RENDER CALLBACKS FOR FLOATING WINDOWS
# -------------------------------------------------------------

def drawShiftGL(deltaT):
    global rpms, maxRpm, scale_shift, show_rpm
    if not show_rpm or maxRpm <= 0:
        return

    try:
        pct = float(rpms) / float(maxRpm)
        if pct > 1.0: pct = 1.0
        if pct < 0.0: pct = 0.0

        total_segments = 24
        segment_gap = 2
        bar_w = 480 * scale_shift
        segment_width = (bar_w - (segment_gap * scale_shift * (total_segments - 1))) / total_segments
        active_segments = int(round(pct * total_segments))

        is_flashing = (pct >= 0.92) and (int(rpms * 0.1) % 2 == 0)

        for i in range(total_segments):
            x = i * (segment_width + (segment_gap * scale_shift))
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
            ac.glQuad(int(x), 0, int(segment_width), int(12 * scale_shift))
    except Exception as e:
        log_error("drawShiftGL failed:\n" + traceback.format_exc())

def drawTiresGL(deltaT):
    global tireTemps, scale_tires, show_chassis, show_tire_bars, brakeTemps
    try:
        # Tires (FL, FR, RL, RR)
        # FL
        col = getTireColor(tireTemps[0])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(80 * scale_tires)), int(round(10 * scale_tires)), int(round(14 * scale_tires)), int(round(26 * scale_tires)))

        # FR
        col = getTireColor(tireTemps[1])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(168 * scale_tires)), int(round(10 * scale_tires)), int(round(14 * scale_tires)), int(round(26 * scale_tires)))

        # RL
        col = getTireColor(tireTemps[2])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(80 * scale_tires)), int(round(60 * scale_tires)), int(round(14 * scale_tires)), int(round(26 * scale_tires)))

        # RR
        col = getTireColor(tireTemps[3])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(round(168 * scale_tires)), int(round(60 * scale_tires)), int(round(14 * scale_tires)), int(round(26 * scale_tires)))

        if show_tire_bars:
            # FL Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(80 * scale_tires)), int(round(39 * scale_tires)), int(round(20 * scale_tires)), int(round(4 * scale_tires)))
            col = getTireColor(tireTemps[0])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[0]) - 40.0) / 80.0))
            ac.glQuad(int(round(80 * scale_tires)), int(round(39 * scale_tires)), int(round(20 * pct * scale_tires)), int(round(4 * scale_tires)))

            # FR Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(168 * scale_tires)), int(round(39 * scale_tires)), int(round(20 * scale_tires)), int(round(4 * scale_tires)))
            col = getTireColor(tireTemps[1])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[1]) - 40.0) / 80.0))
            ac.glQuad(int(round(168 * scale_tires)), int(round(39 * scale_tires)), int(round(20 * pct * scale_tires)), int(round(4 * scale_tires)))

            # RL Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(80 * scale_tires)), int(round(89 * scale_tires)), int(round(20 * scale_tires)), int(round(4 * scale_tires)))
            col = getTireColor(tireTemps[2])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[2]) - 40.0) / 80.0))
            ac.glQuad(int(round(80 * scale_tires)), int(round(89 * scale_tires)), int(round(20 * pct * scale_tires)), int(round(4 * scale_tires)))

            # RR Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(round(168 * scale_tires)), int(round(89 * scale_tires)), int(round(20 * scale_tires)), int(round(4 * scale_tires)))
            col = getTireColor(tireTemps[3])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (float(tireTemps[3]) - 40.0) / 80.0))
            ac.glQuad(int(round(168 * scale_tires)), int(round(89 * scale_tires)), int(round(20 * pct * scale_tires)), int(round(4 * scale_tires)))

        # Brake Indicator Bars
        ac.glColor4f(1.0, 0.2, 0.2, 0.8)
        bf_pct = max(0.0, min(1.0, float(brakeTemps[0]) / 800.0))
        ac.glQuad(int(round(265 * scale_tires)), int(round(20 * scale_tires)), int(round(30 * bf_pct * scale_tires)), int(round(5 * scale_tires)))
        br_pct = max(0.0, min(1.0, float(brakeTemps[2]) / 800.0))
        ac.glQuad(int(round(265 * scale_tires)), int(round(70 * scale_tires)), int(round(30 * br_pct * scale_tires)), int(round(5 * scale_tires)))
    except Exception as e:
        log_error("drawTiresGL failed:\n" + traceback.format_exc())

def drawSpeedGL(deltaT):
    global scale_speed, speed, text_color_idx
    try:
        # Draw Speedometer Circular Gauge Track (0 to 300 KM/H)
        ac.glColor4f(0.15, 0.15, 0.15, 0.8)
        cx, cy = 70.0, 48.0
        r = 46.0
        for deg in range(-220, 40, 3):
            rad = math.radians(deg)
            px = int(round((cx + r * math.cos(rad)) * scale_speed))
            py = int(round((cy + r * math.sin(rad)) * scale_speed))
            ac.glQuad(px - int(round(2 * scale_speed)), py - int(round(2 * scale_speed)), int(round(4 * scale_speed)), int(round(4 * scale_speed)))

        # Draw Active Speedometer Gauge Arc (Colored)
        c = TEXT_COLORS[text_color_idx]
        ac.glColor4f(c[0], c[1], c[2], 0.9)
        speed_pct = max(0.0, min(1.0, float(speed) / 300.0))
        active_deg = int(round(speed_pct * 260.0))
        
        for deg in range(-220, -220 + active_deg, 3):
            rad = math.radians(deg)
            px = int(round((cx + r * math.cos(rad)) * scale_speed))
            py = int(round((cy + r * math.sin(rad)) * scale_speed))
            ac.glQuad(px - int(round(2 * scale_speed)), py - int(round(2 * scale_speed)), int(round(4 * scale_speed)), int(round(4 * scale_speed)))
            
    except Exception as e:
        log_error("drawSpeedGL failed:\n" + traceback.format_exc())

def drawPedalsGL(deltaT):
    global scale_pedals, clutchInput, brakeInput, throttleInput
    try:
        # Fills backgrounds
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(round(50 * scale_pedals)), int(round(7 * scale_pedals)), int(round(65 * scale_pedals)), int(round(8 * scale_pedals)))
        ac.glQuad(int(round(50 * scale_pedals)), int(round(25 * scale_pedals)), int(round(65 * scale_pedals)), int(round(8 * scale_pedals)))
        ac.glQuad(int(round(50 * scale_pedals)), int(round(43 * scale_pedals)), int(round(65 * scale_pedals)), int(round(8 * scale_pedals)))

        # Fill: Clutch
        ac.glColor4f(0.0, 0.5, 1.0, 0.9)
        ac.glQuad(int(round(50 * scale_pedals)), int(round(7 * scale_pedals)), int(round(65 * clutchInput * scale_pedals)), int(round(8 * scale_pedals)))

        # Fill: Brake
        ac.glColor4f(1.0, 0.2, 0.2, 0.9)
        ac.glQuad(int(round(50 * scale_pedals)), int(round(25 * scale_pedals)), int(round(65 * brakeInput * scale_pedals)), int(round(8 * scale_pedals)))

        # Fill: Throttle
        ac.glColor4f(0.0, 1.0, 0.4, 0.9)
        ac.glQuad(int(round(50 * scale_pedals)), int(round(43 * scale_pedals)), int(round(65 * throttleInput * scale_pedals)), int(round(8 * scale_pedals)))
    except Exception as e:
        log_error("drawPedalsGL failed:\n" + traceback.format_exc())

def drawKersGL(deltaT):
    global scale_kers, kersCharge, tyreWear
    try:
        # Kers Inner Bar
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(round(56 * scale_kers)), int(round(4 * scale_kers)), int(round(8 * scale_kers)), int(round(37 * scale_kers)))
        ac.glColor4f(0.0, 0.94, 1.0, 0.9)
        ac.glQuad(int(round(56 * scale_kers)), int(round(4 * scale_kers + (37 * (1.0 - kersCharge)) * scale_kers)), int(round(8 * scale_kers)), int(round(37 * kersCharge * scale_kers)))

        # Wear Inner Bar
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(round(142 * scale_kers)), int(round(4 * scale_kers)), int(round(8 * scale_kers)), int(round(37 * scale_kers)))
        ac.glColor4f(0.6, 0.6, 0.6, 0.9)
        wear_left = max(0.0, min(1.0, 1.0 - tyreWear))
        ac.glQuad(int(round(142 * scale_kers)), int(round(4 * scale_kers + (37 * (1.0 - wear_left)) * scale_kers)), int(round(8 * scale_kers)), int(round(37 * wear_left * scale_kers)))
    except Exception as e:
        log_error("drawKersGL failed:\n" + traceback.format_exc())

def drawTimesGL(deltaT):
    pass

def drawFuelGL(deltaT):
    pass

def acUpdate(deltaT):
    global gear, speed, rpms, fuel, tireTemps, tirePressures, maxRpm
    global scale_shift, scale_tires, scale_speed, scale_gear, scale_pedals, scale_kers, scale_times, scale_fuel, scale_perf, scale_damage, scale_track, scale_debug
    global lblGear, lblSpeed, lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR, lblGForce
    global clutchInput, brakeInput, throttleInput, kersCharge, tyreWear, brakeTemps, gForceLat, gForceLon
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblTimesCurrent, lblTimesBest, lblTimesLast, lblTimesLaps
    global lblFuelCurrent, lblFuelCons, lblFuelEst, lblFuelTemps
    global lblPerfDelta, lblPerfTurbo, lblPerfDRS
    global lblDamageEngine, lblDamageAero, lblDamageTrans
    global lblTrackGrip, lblTrackWind
    global last_lap_completed, fuel_at_lap_start, fuel_consumptions, fuel_per_lap_avg
    global last_opacity_value, sliderOpacity, lblOpacityName, opacity_pct
    global last_bg_color_value, sliderBgColor, lblBgColorName, bg_color_idx
    global last_text_color_value, sliderTextColor, lblTextColorName, text_color_idx
    global sliderScaleShift, sliderScaleTires, sliderScaleSpeed, sliderScaleGear, sliderScalePedals, sliderScaleKers, sliderScaleTimes, sliderScaleFuel, sliderScalePerf, sliderScaleDamage, sliderScaleTrack, sliderScaleDebug
    global last_scale_shift, last_scale_tires, last_scale_speed, last_scale_gear, last_scale_pedals, last_scale_kers, last_scale_times, last_scale_fuel, last_scale_perf, last_scale_damage, last_scale_track, last_scale_debug

    # 0. Check in-game Scale, Opacity, and Colors Spinners
    try:
        # 12 scale sliders
        if sliderScaleShift != 0:
            val = int(round(ac.getValue(sliderScaleShift)))
            if val != last_scale_shift:
                last_scale_shift = val
                updateScaleShift(val / 100.0)
                saveConfig()
        if sliderScaleTires != 0:
            val = int(round(ac.getValue(sliderScaleTires)))
            if val != last_scale_tires:
                last_scale_tires = val
                updateScaleTires(val / 100.0)
                saveConfig()
        if sliderScaleSpeed != 0:
            val = int(round(ac.getValue(sliderScaleSpeed)))
            if val != last_scale_speed:
                last_scale_speed = val
                updateScaleSpeed(val / 100.0)
                saveConfig()
        if sliderScaleGear != 0:
            val = int(round(ac.getValue(sliderScaleGear)))
            if val != last_scale_gear:
                last_scale_gear = val
                updateScaleGear(val / 100.0)
                saveConfig()
        if sliderScalePedals != 0:
            val = int(round(ac.getValue(sliderScalePedals)))
            if val != last_scale_pedals:
                last_scale_pedals = val
                updateScalePedals(val / 100.0)
                saveConfig()
        if sliderScaleKers != 0:
            val = int(round(ac.getValue(sliderScaleKers)))
            if val != last_scale_kers:
                last_scale_kers = val
                updateScaleKers(val / 100.0)
                saveConfig()
        if sliderScaleTimes != 0:
            val = int(round(ac.getValue(sliderScaleTimes)))
            if val != last_scale_times:
                last_scale_times = val
                updateScaleTimes(val / 100.0)
                saveConfig()
        if sliderScaleFuel != 0:
            val = int(round(ac.getValue(sliderScaleFuel)))
            if val != last_scale_fuel:
                last_scale_fuel = val
                updateScaleFuel(val / 100.0)
                saveConfig()
        if sliderScalePerf != 0:
            val = int(round(ac.getValue(sliderScalePerf)))
            if val != last_scale_perf:
                last_scale_perf = val
                updateScalePerf(val / 100.0)
                saveConfig()
        if sliderScaleDamage != 0:
            val = int(round(ac.getValue(sliderScaleDamage)))
            if val != last_scale_damage:
                last_scale_damage = val
                updateScaleDamage(val / 100.0)
                saveConfig()
        if sliderScaleTrack != 0:
            val = int(round(ac.getValue(sliderScaleTrack)))
            if val != last_scale_track:
                last_scale_track = val
                updateScaleTrack(val / 100.0)
                saveConfig()
        if sliderScaleDebug != 0:
            val = int(round(ac.getValue(sliderScaleDebug)))
            if val != last_scale_debug:
                last_scale_debug = val
                updateScaleDebug(val / 100.0)
                saveConfig()

        # Opacity
        if sliderOpacity != 0:
            current_op = int(round(ac.getValue(sliderOpacity)))
            if current_op != last_opacity_value:
                last_opacity_value = current_op
                opacity_pct = current_op
                ac.setText(lblOpacityName, "HUD Opacity: {0}%".format(current_op))
                updateWindowsBackground()
                saveConfig()

        # BG Color Theme
        if sliderBgColor != 0:
            current_bg = int(round(ac.getValue(sliderBgColor)))
            if current_bg != last_bg_color_value:
                last_bg_color_value = current_bg
                bg_color_idx = current_bg
                ac.setText(lblBgColorName, "BG Theme (0-3): {0}".format(current_bg))
                updateWindowsBackground()
                saveConfig()

        # Text Color Theme
        if sliderTextColor != 0:
            current_txt = int(round(ac.getValue(sliderTextColor)))
            if current_txt != last_text_color_value:
                last_text_color_value = current_txt
                text_color_idx = current_txt
                ac.setText(lblTextColorName, "Text Theme (0-4): {0}".format(current_txt))
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

        # Performance & Turbo & DRS update
        try:
            turbo = simInfo.physics.turboBoost
            drs_enabled = simInfo.physics.drsEnabled
            drs_avail = simInfo.physics.drsAvailable
            
            ac.setText(lblPerfTurbo, "Turbo: {0:.1f} bar".format(turbo))
            if drs_enabled:
                ac.setText(lblPerfDRS, "DRS: ON")
            elif drs_avail:
                ac.setText(lblPerfDRS, "DRS: AVL")
            else:
                ac.setText(lblPerfDRS, "DRS: N/A")
        except Exception as e:
            log_error("Performance SM update failed:\n" + traceback.format_exc())

        # Damage update
        try:
            aero_dmg = max(simInfo.physics.carDamage[0], simInfo.physics.carDamage[1], simInfo.physics.carDamage[2]) * 100.0
            eng_dmg = simInfo.physics.carDamage[3] * 100.0
            trans_dmg = simInfo.physics.carDamage[4] * 100.0
            
            ac.setText(lblDamageAero, "Aero: {0:.0f}%".format(aero_dmg))
            ac.setText(lblDamageEngine, "Eng: {0:.0f}%".format(100.0 - eng_dmg))
            ac.setText(lblDamageTrans, "Gear: {0:.0f}%".format(100.0 - trans_dmg))
        except Exception as e:
            log_error("Damage SM update failed:\n" + traceback.format_exc())

        # Track Weather & Wind update
        try:
            grip = simInfo.graphics.surfaceGrip * 100.0
            wind_s = simInfo.graphics.windSpeed * 3.6 # convert m/s to km/h
            ac.setText(lblTrackGrip, "Grip: {0:.1f}%".format(grip))
            ac.setText(lblTrackWind, "Wind: {0:.1f} km/h".format(wind_s))
        except Exception as e:
            log_error("Track SM update failed:\n" + traceback.format_exc())

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

    # Performance Live Delta update via API (CS.PerformanceMeter is Kunos native delta value)
    try:
        delta = ac.getCarState(0, acsys.CS.PerformanceMeter)
        ac.setText(lblPerfDelta, "{0:+.2f}".format(delta))
    except Exception as e:
        log_error("Delta update failed:\n" + traceback.format_exc())

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
