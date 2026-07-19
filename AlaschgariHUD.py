# AlaschgariHUD for Assetto Corsa
# Modular Sidekick Replica HUD - 5 separate floating apps + In-Game scale settings

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

# Scale factor from configuration
scale = 1.0

# 6 App Windows
appShift = 0
appTires = 0
appSpeed = 0
appPedals = 0
appKers = 0
appSettings = 0

# UI Controls
lblGear = 0
lblGearLabel = 0
lblSpeed = 0
lblSpeedLabel = 0
lblGForce = 0
lblPressFL = 0
lblPressFR = 0
lblPressRL = 0
lblPressRR = 0
lblBrakeF = 0
lblBrakeR = 0

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

lblSliderName = 0
sliderScale = 0
last_spinner_value = 100.0

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

# Settings file variables
show_rpm = True
show_chassis = True
show_tire_bars = True

def getConfigPath():
    return os.path.join(os.path.dirname(__file__), 'config.ini')

def loadConfig():
    global scale, show_rpm, show_chassis, show_tire_bars
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
    except Exception as e:
        log_error("saveConfig failed: " + str(e))

def updateScale(new_scale):
    global scale
    global appShift, appTires, appSpeed, appPedals, appKers
    global lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR
    global lblSpeed, lblSpeedLabel, lblGear, lblGearLabel, lblGForce
    global lblPedalClutch, lblPedalBrake, lblPedalThrottle, lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblKersName, lblWearName

    scale = new_scale
    
    # 1. Resize all modular windows
    ac.setSize(appShift, int(480 * scale), int(20 * scale))
    ac.setSize(appTires, int(310 * scale), int(112 * scale))
    ac.setSize(appSpeed, int(290 * scale), int(112 * scale))
    ac.setSize(appPedals, int(162 * scale), int(70 * scale))
    ac.setSize(appKers, int(162 * scale), int(45 * scale))

    # 2. Update Tires label positions and fonts
    ac.setPosition(lblPressFL, int(15 * scale), int(22 * scale))
    ac.setFontSize(lblPressFL, int(11 * scale))
    ac.setPosition(lblPressRL, int(15 * scale), int(72 * scale))
    ac.setFontSize(lblPressRL, int(11 * scale))
    ac.setPosition(lblPressFR, int(212 * scale), int(22 * scale))
    ac.setFontSize(lblPressFR, int(11 * scale))
    ac.setPosition(lblPressRR, int(212 * scale), int(72 * scale))
    ac.setFontSize(lblPressRR, int(11 * scale))
    ac.setPosition(lblBrakeF, int(265 * scale), int(22 * scale))
    ac.setFontSize(lblBrakeF, int(13 * scale))
    ac.setPosition(lblBrakeR, int(265 * scale), int(72 * scale))
    ac.setFontSize(lblBrakeR, int(13 * scale))

    # 3. Update Speed label positions and fonts
    ac.setPosition(lblSpeed, int(70 * scale), int(42 * scale))
    ac.setFontSize(lblSpeed, int(28 * scale))
    ac.setPosition(lblSpeedLabel, int(70 * scale), int(105 * scale))
    ac.setFontSize(lblSpeedLabel, int(8 * scale))
    ac.setPosition(lblGear, int(215 * scale), int(34 * scale))
    ac.setFontSize(lblGear, int(24 * scale))
    ac.setPosition(lblGForce, int(215 * scale), int(75 * scale))
    ac.setFontSize(lblGForce, int(9 * scale))
    ac.setPosition(lblGearLabel, int(215 * scale), int(105 * scale))
    ac.setFontSize(lblGearLabel, int(8 * scale))

    # 4. Update Pedals label positions and fonts
    ac.setPosition(lblPedalClutch, int(8 * scale), int(5 * scale))
    ac.setFontSize(lblPedalClutch, int(8 * scale))
    ac.setPosition(lblPedalBrake, int(8 * scale), int(23 * scale))
    ac.setFontSize(lblPedalBrake, int(8 * scale))
    ac.setPosition(lblPedalThrottle, int(8 * scale), int(41 * scale))
    ac.setFontSize(lblPedalThrottle, int(8 * scale))
    ac.setPosition(lblPedalClutchVal, int(154 * scale), int(5 * scale))
    ac.setFontSize(lblPedalClutchVal, int(8 * scale))
    ac.setPosition(lblPedalBrakeVal, int(154 * scale), int(23 * scale))
    ac.setFontSize(lblPedalBrakeVal, int(8 * scale))
    ac.setPosition(lblPedalThrottleVal, int(154 * scale), int(41 * scale))
    ac.setFontSize(lblPedalThrottleVal, int(8 * scale))

    # 5. Update KERS label positions and fonts
    ac.setPosition(lblKersName, int(12 * scale), int(16 * scale))
    ac.setFontSize(lblKersName, int(9 * scale))
    ac.setPosition(lblWearName, int(90 * scale), int(16 * scale))
    ac.setFontSize(lblWearName, int(9 * scale))

def onScaleSliderChange(value):
    global scale, lblSliderName
    new_scale = value / 100.0
    updateScale(new_scale)
    ac.setText(lblSliderName, "HUD Scale: {0:.0f}%".format(value))
    saveConfig()

def acMain(ac_version):
    global scale, lblDebugError
    global appShift, appTires, appSpeed, appPedals, appKers, appSettings
    global lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR
    global lblSpeed, lblSpeedLabel, lblGear, lblGearLabel, lblGForce
    global lblPedalClutch, lblPedalBrake, lblPedalThrottle, lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblKersName, lblWearName, lblSliderName, sliderScale

    try:
        loadConfig()

        # ---------------------------------------------
        # 1. APP: SHIFT LIGHT BAR (480px x 20px)
        # ---------------------------------------------
        appShift = ac.newApp("AlaschgariHUD - Shift Lights")
        ac.setSize(appShift, int(480 * scale), int(20 * scale))
        ac.setTitle(appShift, "")
        ac.drawBorder(appShift, 0)
        ac.setBackgroundOpacity(appShift, 0.0)
        ac.setIconPosition(appShift, -10000, -10000)
        ac.addRenderCallback(appShift, drawShiftGL)

        # ---------------------------------------------
        # 2. APP: TIRES & BRAKES STATUS (310px x 112px)
        # ---------------------------------------------
        appTires = ac.newApp("AlaschgariHUD - Tires & Brakes")
        ac.setSize(appTires, int(310 * scale), int(112 * scale))
        ac.setTitle(appTires, "")
        ac.drawBorder(appTires, 0)
        ac.setBackgroundOpacity(appTires, 0.0)
        ac.setIconPosition(appTires, -10000, -10000)
        ac.addRenderCallback(appTires, drawTiresGL)

        # Labels
        lblPressFL = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressFL, int(15 * scale), int(22 * scale))
        ac.setFontSize(lblPressFL, int(11 * scale))

        lblPressRL = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressRL, int(15 * scale), int(72 * scale))
        ac.setFontSize(lblPressRL, int(11 * scale))

        lblPressFR = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressFR, int(212 * scale), int(22 * scale))
        ac.setFontSize(lblPressFR, int(11 * scale))
        ac.setFontAlignment(lblPressFR, "right")

        lblPressRR = ac.addLabel(appTires, "0\n0.0")
        ac.setPosition(lblPressRR, int(212 * scale), int(72 * scale))
        ac.setFontSize(lblPressRR, int(11 * scale))
        ac.setFontAlignment(lblPressRR, "right")

        lblBrakeF = ac.addLabel(appTires, "0")
        ac.setPosition(lblBrakeF, int(265 * scale), int(22 * scale))
        ac.setFontSize(lblBrakeF, int(13 * scale))
        ac.setFontColor(lblBrakeF, 1.0, 0.2, 0.2, 1.0)

        lblBrakeR = ac.addLabel(appTires, "0")
        ac.setPosition(lblBrakeR, int(265 * scale), int(72 * scale))
        ac.setFontSize(lblBrakeR, int(13 * scale))
        ac.setFontColor(lblBrakeR, 1.0, 0.2, 0.2, 1.0)

        # ---------------------------------------------
        # 3. APP: SPEEDOMETER & GEAR (290px x 112px)
        # ---------------------------------------------
        appSpeed = ac.newApp("AlaschgariHUD - Speed & Gear")
        ac.setSize(appSpeed, int(290 * scale), int(112 * scale))
        ac.setTitle(appSpeed, "")
        ac.drawBorder(appSpeed, 0)
        ac.setBackgroundOpacity(appSpeed, 0.0)
        ac.setIconPosition(appSpeed, -10000, -10000)
        ac.addRenderCallback(appSpeed, drawSpeedGL)

        lblSpeed = ac.addLabel(appSpeed, "0 KM/H")
        ac.setPosition(lblSpeed, int(70 * scale), int(42 * scale))
        ac.setFontSize(lblSpeed, int(28 * scale))
        ac.setFontAlignment(lblSpeed, "center")
        ac.setFontColor(lblSpeed, 0.0, 0.94, 1.0, 1.0)

        lblSpeedLabel = ac.addLabel(appSpeed, "Speedometer")
        ac.setPosition(lblSpeedLabel, int(70 * scale), int(105 * scale))
        ac.setFontSize(lblSpeedLabel, int(8 * scale))
        ac.setFontAlignment(lblSpeedLabel, "center")
        ac.setFontColor(lblSpeedLabel, 0.4, 0.4, 0.4, 1.0)

        lblGear = ac.addLabel(appSpeed, "G1")
        ac.setPosition(lblGear, int(215 * scale), int(34 * scale))
        ac.setFontSize(lblGear, int(24 * scale))
        ac.setFontAlignment(lblGear, "center")

        lblGForce = ac.addLabel(appSpeed, "0.00 / 0.00")
        ac.setPosition(lblGForce, int(215 * scale), int(75 * scale))
        ac.setFontSize(lblGForce, int(9 * scale))
        ac.setFontAlignment(lblGForce, "center")
        ac.setFontColor(lblGForce, 0.0, 0.94, 1.0, 1.0)

        lblGearLabel = ac.addLabel(appSpeed, "G-Force / Gear")
        ac.setPosition(lblGearLabel, int(215 * scale), int(105 * scale))
        ac.setFontSize(lblGearLabel, int(8 * scale))
        ac.setFontAlignment(lblGearLabel, "center")
        ac.setFontColor(lblGearLabel, 0.4, 0.4, 0.4, 1.0)

        # ---------------------------------------------
        # 4. APP: PEDAL INPUTS (162px x 70px)
        # ---------------------------------------------
        appPedals = ac.newApp("AlaschgariHUD - Pedals")
        ac.setSize(appPedals, int(162 * scale), int(70 * scale))
        ac.setTitle(appPedals, "")
        ac.drawBorder(appPedals, 0)
        ac.setBackgroundOpacity(appPedals, 0.0)
        ac.setIconPosition(appPedals, -10000, -10000)
        ac.addRenderCallback(appPedals, drawPedalsGL)

        lblPedalClutch = ac.addLabel(appPedals, "Clutch")
        ac.setPosition(lblPedalClutch, int(8 * scale), int(5 * scale))
        ac.setFontSize(lblPedalClutch, int(8 * scale))

        lblPedalBrake = ac.addLabel(appPedals, "Brake")
        ac.setPosition(lblPedalBrake, int(8 * scale), int(23 * scale))
        ac.setFontSize(lblPedalBrake, int(8 * scale))

        lblPedalThrottle = ac.addLabel(appPedals, "Throt")
        ac.setPosition(lblPedalThrottle, int(8 * scale), int(41 * scale))
        ac.setFontSize(lblPedalThrottle, int(8 * scale))

        lblPedalClutchVal = ac.addLabel(appPedals, "0%")
        ac.setPosition(lblPedalClutchVal, int(154 * scale), int(5 * scale))
        ac.setFontSize(lblPedalClutchVal, int(8 * scale))
        ac.setFontAlignment(lblPedalClutchVal, "right")

        lblPedalBrakeVal = ac.addLabel(appPedals, "0%")
        ac.setPosition(lblPedalBrakeVal, int(154 * scale), int(23 * scale))
        ac.setFontSize(lblPedalBrakeVal, int(8 * scale))
        ac.setFontAlignment(lblPedalBrakeVal, "right")

        lblPedalThrottleVal = ac.addLabel(appPedals, "0%")
        ac.setPosition(lblPedalThrottleVal, int(154 * scale), int(41 * scale))
        ac.setFontSize(lblPedalThrottleVal, int(8 * scale))
        ac.setFontAlignment(lblPedalThrottleVal, "right")

        # ---------------------------------------------
        # 5. APP: KERS & TIRE WEAR (162px x 45px)
        # ---------------------------------------------
        appKers = ac.newApp("AlaschgariHUD - KERS & Wear")
        ac.setSize(appKers, int(162 * scale), int(45 * scale))
        ac.setTitle(appKers, "")
        ac.drawBorder(appKers, 0)
        ac.setBackgroundOpacity(appKers, 0.0)
        ac.setIconPosition(appKers, -10000, -10000)
        ac.addRenderCallback(appKers, drawKersGL)

        lblKersName = ac.addLabel(appKers, "KERS")
        ac.setPosition(lblKersName, int(12 * scale), int(16 * scale))
        ac.setFontSize(lblKersName, int(9 * scale))

        lblWearName = ac.addLabel(appKers, "WEAR")
        ac.setPosition(lblWearName, int(90 * scale), int(16 * scale))
        ac.setFontSize(lblWearName, int(9 * scale))

        # Setup main debug label in tires app window as anchor
        lblDebugError = ac.addLabel(appTires, "")
        ac.setPosition(lblDebugError, int(10 * scale), int(115 * scale))
        ac.setFontSize(lblDebugError, int(8 * scale))
        ac.setFontColor(lblDebugError, 1.0, 0.2, 0.2, 1.0)

        # ---------------------------------------------
        # 6. APP: HUD IN-GAME CONFIG WINDOW
        # ---------------------------------------------
        appSettings = ac.newApp("AlaschgariHUD - Config")
        ac.setSize(appSettings, 250, 80)
        ac.setTitle(appSettings, "AlaschgariHUD Options")
        
        lblSliderName = ac.addLabel(appSettings, "HUD Scale: {0:.0f}%".format(scale * 100))
        ac.setPosition(lblSliderName, 10, 10)
        ac.setFontSize(lblSliderName, 10)

        sliderScale = ac.addSpinner(appSettings, "Scale")
        ac.setPosition(sliderScale, 10, 35)
        ac.setSize(sliderScale, 230, 20)
        ac.setRange(sliderScale, 50, 150)
        ac.setStep(sliderScale, 5)
        ac.setValue(sliderScale, int(scale * 100))
        
        last_spinner_value = int(scale * 100)

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
        # Panel Background
        ac.glColor4f(0.08, 0.09, 0.12, 0.65)
        ac.glQuad(0, 0, int(round(310 * scale)), int(round(112 * scale)))

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
    global scale
    try:
        # Background Boxes
        ac.glColor4f(0.08, 0.09, 0.12, 0.65)
        # Speedometer Box (width 140)
        ac.glQuad(0, 0, int(140 * scale), int(112 * scale))
        # Gear / G-Force Box (width 140, offset 150)
        ac.glQuad(int(150 * scale), 0, int(140 * scale), int(112 * scale))
    except Exception as e:
        log_error("drawSpeedGL failed:\n" + traceback.format_exc())

def drawPedalsGL(deltaT):
    global scale, clutchInput, brakeInput, throttleInput
    try:
        # Background Box
        ac.glColor4f(0.08, 0.09, 0.12, 0.65)
        ac.glQuad(0, 0, int(162 * scale), int(70 * scale))

        # Fills backgrounds
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(50 * scale), int(7 * scale), int(65 * scale), int(8 * scale))
        ac.glQuad(int(50 * scale), int(25 * scale), int(65 * scale), int(8 * scale))
        ac.glQuad(int(50 * scale), int(43 * scale), int(65 * scale), int(8 * scale))

        # Fill: Clutch
        ac.glColor4f(0.0, 0.5, 1.0, 0.9)
        ac.glQuad(int(50 * scale), int(7 * scale), int(65 * clutchInput * scale), int(8 * scale))

        # Fill: Brake
        ac.glColor4f(1.0, 0.2, 0.2, 0.9)
        ac.glQuad(int(50 * scale), int(25 * scale), int(65 * brakeInput * scale), int(8 * scale))

        # Fill: Throttle
        ac.glColor4f(0.0, 1.0, 0.4, 0.9)
        ac.glQuad(int(50 * scale), int(43 * scale), int(65 * throttleInput * scale), int(8 * scale))
    except Exception as e:
        log_error("drawPedalsGL failed:\n" + traceback.format_exc())

def drawKersGL(deltaT):
    global scale, kersCharge, tyreWear
    try:
        # Background Boxes
        ac.glColor4f(0.08, 0.09, 0.12, 0.65)
        ac.glQuad(0, 0, int(76 * scale), int(45 * scale))
        ac.glQuad(int(86 * scale), 0, int(76 * scale), int(45 * scale))

        # Kers Inner Bar
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(56 * scale), int(4 * scale), int(8 * scale), int(37 * scale))
        ac.glColor4f(0.0, 0.94, 1.0, 0.9)
        ac.glQuad(int(56 * scale), int(4 * scale + (37 * (1.0 - kersCharge)) * scale), int(8 * scale), int(37 * kersCharge * scale))

        # Wear Inner Bar
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(142 * scale), int(4 * scale), int(8 * scale), int(37 * scale))
        ac.glColor4f(0.6, 0.6, 0.6, 0.9)
        wear_left = max(0.0, min(1.0, 1.0 - tyreWear))
        ac.glQuad(int(142 * scale), int(4 * scale + (37 * (1.0 - wear_left)) * scale), int(8 * scale), int(37 * wear_left * scale))
    except Exception as e:
        log_error("drawKersGL failed:\n" + traceback.format_exc())

def acUpdate(deltaT):
    global gear, speed, rpms, fuel, tireTemps, tirePressures, maxRpm, scale
    global lblGear, lblSpeed, lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR, lblGForce
    global clutchInput, brakeInput, throttleInput, kersCharge, tyreWear, brakeTemps, gForceLat, gForceLon
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global last_spinner_value, sliderScale, lblSliderName

    # 0. Check in-game Scale Spinner
    try:
        if sliderScale != 0:
            current_val = ac.getValue(sliderScale)
            if current_val != last_spinner_value:
                last_spinner_value = current_val
                updateScale(current_val / 100.0)
                ac.setText(lblSliderName, "HUD Scale: {0:.0f}%".format(current_val))
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
            kersCharge = simInfo.physics.ersDelivery
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
