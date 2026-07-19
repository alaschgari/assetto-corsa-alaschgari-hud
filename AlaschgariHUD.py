# AlaschgariHUD for Assetto Corsa
# Double-width Sidekick Replica HUD with full telemetry and CM Settings

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

# UI Controls (Forward declared for log_error visibility)
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

# App configuration (800px x 140px replica layout)
appName = "AlaschgariHUD"
width, height = 800, 140

# Settings variables with defaults
active_skin = "default"
scale = 1.0
show_rpm = True
show_chassis = True
show_tire_bars = True

# UI Controls
lblGear = 0
lblGearBoxLabel = 0
lblSpeed = 0
lblSpeedBoxLabel = 0
lblGForce = 0
lblPressFL = 0
lblPressFR = 0
lblPressRL = 0
lblPressRR = 0
lblBrakeF = 0
lblBrakeR = 0

# Pedal label overlays
lblPedalClutchVal = 0
lblPedalBrakeVal = 0
lblPedalThrottleVal = 0

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

def getConfigPath():
    return os.path.join(os.path.dirname(__file__), 'config.ini')

def loadConfig():
    global active_skin, scale, show_rpm, show_chassis, show_tire_bars
    path = getConfigPath()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k == 'skin':
                            active_skin = v.lower()
                        elif k == 'scale':
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
            f.write("skin = " + active_skin + "\n")
            f.write("scale = " + str(int(scale * 100)) + "\n")
            f.write("show_rpm = " + str(show_rpm) + "\n")
            f.write("show_chassis = " + str(show_chassis) + "\n")
            f.write("show_tire_bars = " + str(show_tire_bars) + "\n")
    except Exception as e:
        log_error("saveConfig failed: " + str(e))

def applySkin():
    global appWindow, lblGear, lblSpeed, scale
    try:
        ac.setBackgroundOpacity(appWindow, 0.6)
        ac.setBackgroundColor(appWindow, 0.08, 0.09, 0.12)
    except Exception as e:
        log_error("applySkin failed: " + traceback.format_exc())

def acMain(ac_version):
    global appWindow, lblGear, lblSpeed, scale, lblDebugError
    global lblPressFL, lblPressFR, lblPressRL, lblPressRR
    global lblBrakeF, lblBrakeR, lblGForce, lblGearBoxLabel, lblSpeedBoxLabel
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal

    try:
        loadConfig()

        appWindow = ac.newApp(appName)
        ac.setTitle(appWindow, "")
        ac.setSize(appWindow, int(width * scale), int(height * scale))
        ac.drawBorder(appWindow, 0)
        ac.setIconPosition(appWindow, -10000, -10000)

        # ---------------------------------------------
        # LEFT PANEL: Tire & Brake Status (x=10 to x=320)
        # ---------------------------------------------
        
        # Temp/Pressure labels
        lblPressFL = ac.addLabel(appWindow, "0\n0.0")
        ac.setPosition(lblPressFL, int(15 * scale), int(22 * scale))
        ac.setFontSize(lblPressFL, int(11 * scale))

        lblPressRL = ac.addLabel(appWindow, "0\n0.0")
        ac.setPosition(lblPressRL, int(15 * scale), int(72 * scale))
        ac.setFontSize(lblPressRL, int(11 * scale))

        lblPressFR = ac.addLabel(appWindow, "0\n0.0")
        ac.setPosition(lblPressFR, int(212 * scale), int(22 * scale))
        ac.setFontSize(lblPressFR, int(11 * scale))
        ac.setFontAlignment(lblPressFR, "right")

        lblPressRR = ac.addLabel(appWindow, "0\n0.0")
        ac.setPosition(lblPressRR, int(212 * scale), int(72 * scale))
        ac.setFontSize(lblPressRR, int(11 * scale))
        ac.setFontAlignment(lblPressRR, "right")

        # Brakes (Front and Rear labels)
        lblBrakeF = ac.addLabel(appWindow, "0")
        ac.setPosition(lblBrakeF, int(265 * scale), int(22 * scale))
        ac.setFontSize(lblBrakeF, int(13 * scale))
        ac.setFontColor(lblBrakeF, 1.0, 0.2, 0.2, 1.0)

        lblBrakeR = ac.addLabel(appWindow, "0")
        ac.setPosition(lblBrakeR, int(265 * scale), int(72 * scale))
        ac.setFontSize(lblBrakeR, int(13 * scale))
        ac.setFontColor(lblBrakeR, 1.0, 0.2, 0.2, 1.0)

        # ---------------------------------------------
        # CENTER PANEL: Speedometer & Gear Box (x=340 to x=610)
        # ---------------------------------------------

        # Speedometer Box Label (SPEEDOMETER)
        lblSpeedBoxLabel = ac.addLabel(appWindow, "Speedometer")
        ac.setPosition(lblSpeedBoxLabel, int(412 * scale), int(105 * scale))
        ac.setFontSize(lblSpeedBoxLabel, int(8 * scale))
        ac.setFontAlignment(lblSpeedBoxLabel, "center")
        ac.setFontColor(lblSpeedBoxLabel, 0.4, 0.4, 0.4, 1.0)

        # Speed Value Text
        lblSpeed = ac.addLabel(appWindow, "0 KM/H")
        ac.setPosition(lblSpeed, int(412 * scale), int(42 * scale))
        ac.setFontSize(lblSpeed, int(28 * scale))
        ac.setFontAlignment(lblSpeed, "center")
        ac.setFontColor(lblSpeed, 0.0, 0.94, 1.0, 1.0) # Neon cyan

        # Gear/G-Force Box Label (G-FORCE VECTOR)
        lblGearBoxLabel = ac.addLabel(appWindow, "G-Force / Gear")
        ac.setPosition(lblGearBoxLabel, int(547 * scale), int(105 * scale))
        ac.setFontSize(lblGearBoxLabel, int(8 * scale))
        ac.setFontAlignment(lblGearBoxLabel, "center")
        ac.setFontColor(lblGearBoxLabel, 0.4, 0.4, 0.4, 1.0)

        # Gear value (G5 style)
        lblGear = ac.addLabel(appWindow, "G1")
        ac.setPosition(lblGear, int(547 * scale), int(34 * scale))
        ac.setFontSize(lblGear, int(24 * scale))
        ac.setFontAlignment(lblGear, "center")

        # G-Force values
        lblGForce = ac.addLabel(appWindow, "0.00 / 0.00")
        ac.setPosition(lblGForce, int(547 * scale), int(75 * scale))
        ac.setFontSize(lblGForce, int(9 * scale))
        ac.setFontAlignment(lblGForce, "center")
        ac.setFontColor(lblGForce, 0.0, 0.94, 1.0, 1.0)

        # ---------------------------------------------
        # RIGHT PANEL: Pedals, KERS & Wear (x=630 to x=790)
        # ---------------------------------------------

        # Pedal value labels
        lblPedalClutchVal = ac.addLabel(appWindow, "0%")
        ac.setPosition(lblPedalClutchVal, int(755 * scale), int(20 * scale))
        ac.setFontSize(lblPedalClutchVal, int(8 * scale))
        ac.setFontAlignment(lblPedalClutchVal, "right")

        lblPedalBrakeVal = ac.addLabel(appWindow, "0%")
        ac.setPosition(lblPedalBrakeVal, int(755 * scale), int(38 * scale))
        ac.setFontSize(lblPedalBrakeVal, int(8 * scale))
        ac.setFontAlignment(lblPedalBrakeVal, "right")

        lblPedalThrottleVal = ac.addLabel(appWindow, "0%")
        ac.setPosition(lblPedalThrottleVal, int(755 * scale), int(56 * scale))
        ac.setFontSize(lblPedalThrottleVal, int(8 * scale))
        ac.setFontAlignment(lblPedalThrottleVal, "right")

        # ---------------------------------------------
        # GLOBAL SYSTEM: Debug & Rendering
        # ---------------------------------------------

        lblDebugError = ac.addLabel(appWindow, "")
        ac.setPosition(lblDebugError, int(15 * scale), int(115 * scale))
        ac.setFontSize(lblDebugError, int(8 * scale))
        ac.setFontColor(lblDebugError, 1.0, 0.2, 0.2, 1.0)

        applySkin()

        ac.addRenderCallback(appWindow, appGL)

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
    if temp < 70.0:
        return [0.1, 0.4, 0.8, 0.9] # Cold
    elif temp > 95.0:
        return [1.0, 0.0, 0.62, 0.9] # Hot
    else:
        return [0.0, 1.0, 0.4, 0.9] # Optimal green

def appGL(deltaT):
    global rpms, maxRpm, speed, tireTemps, scale, show_rpm, show_chassis, show_tire_bars
    global clutchInput, brakeInput, throttleInput, kersCharge, tyreWear, brakeTemps

    try:
        # 1. DRAW SUB-BACKGROUND PANELS (Boxes)
        # Left Panel (Chassis & Tires)
        ac.glColor4f(0.13, 0.15, 0.19, 0.4)
        ac.glQuad(int(10 * scale), int(18 * scale), int(310 * scale), int(112 * scale))

        # Center Sub Box 1: Speedometer
        ac.glQuad(int(330 * scale), int(18 * scale), int(140 * scale), int(112 * scale))

        # Center Sub Box 2: Gear & G-Force
        ac.glQuad(int(478 * scale), int(18 * scale), int(140 * scale), int(112 * scale))

        # Right Panel (Pedals & Wear)
        ac.glQuad(int(628 * scale), int(18 * scale), int(162 * scale), int(112 * scale))

        # ---------------------------------------------
        # LEFT PANEL: Chassis Axles & Outline
        # ---------------------------------------------
        if show_chassis:
            ac.glColor4f(1.0, 1.0, 1.0, 0.15)
            # Outline Cabin
            ac.glQuad(int(110 * scale), int(28 * scale), int(60 * scale), int(90 * scale))
            # Axles
            ac.glQuad(int(95 * scale), int(48 * scale), int(90 * scale), int(1.5 * scale))
            ac.glQuad(int(95 * scale), int(98 * scale), int(90 * scale), int(1.5 * scale))

        # Draw Tires (FL: x=80, y=28; FR: x=168, y=28)
        # Front Left
        col = getTireColor(tireTemps[0])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(80 * scale), int(28 * scale), int(14 * scale), int(26 * scale))

        # Front Right
        col = getTireColor(tireTemps[1])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(168 * scale), int(28 * scale), int(14 * scale), int(26 * scale))

        # Rear Left
        col = getTireColor(tireTemps[2])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(80 * scale), int(78 * scale), int(14 * scale), int(26 * scale))

        # Rear Right
        col = getTireColor(tireTemps[3])
        ac.glColor4f(col[0], col[1], col[2], col[3])
        ac.glQuad(int(168 * scale), int(78 * scale), int(14 * scale), int(26 * scale))

        # Tire Bars
        if show_tire_bars:
            # FL Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(80 * scale), int(57 * scale), int(20 * scale), int(4 * scale))
            col = getTireColor(tireTemps[0])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (tireTemps[0] - 40.0) / 80.0))
            ac.glQuad(int(80 * scale), int(57 * scale), int(20 * pct * scale), int(4 * scale))

            # FR Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(168 * scale), int(57 * scale), int(20 * scale), int(4 * scale))
            col = getTireColor(tireTemps[1])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (tireTemps[1] - 40.0) / 80.0))
            ac.glQuad(int(168 * scale), int(57 * scale), int(20 * pct * scale), int(4 * scale))

            # RL Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(80 * scale), int(107 * scale), int(20 * scale), int(4 * scale))
            col = getTireColor(tireTemps[2])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (tireTemps[2] - 40.0) / 80.0))
            ac.glQuad(int(80 * scale), int(107 * scale), int(20 * pct * scale), int(4 * scale))

            # RR Bar
            ac.glColor4f(0.05, 0.05, 0.05, 0.9)
            ac.glQuad(int(168 * scale), int(107 * scale), int(20 * scale), int(4 * scale))
            col = getTireColor(tireTemps[3])
            ac.glColor4f(col[0], col[1], col[2], col[3])
            pct = max(0.0, min(1.0, (tireTemps[3] - 40.0) / 80.0))
            ac.glQuad(int(168 * scale), int(107 * scale), int(20 * pct * scale), int(4 * scale))

        # Brake Bars (Red line indicator under brake temps)
        ac.glColor4f(1.0, 0.2, 0.2, 0.8)
        # Front Brake
        bf_pct = max(0.0, min(1.0, brakeTemps[0] / 800.0))
        ac.glQuad(int(265 * scale), int(38 * scale), int(30 * bf_pct * scale), int(5 * scale))
        # Rear Brake
        br_pct = max(0.0, min(1.0, brakeTemps[2] / 800.0))
        ac.glQuad(int(265 * scale), int(88 * scale), int(30 * br_pct * scale), int(5 * scale))

        # ---------------------------------------------
        # RIGHT PANEL: Pedals (Clutch, Brake, Throttle)
        # ---------------------------------------------
        # Names labels Clutch(x=635,y=20), Brake(y=38), Throttle(y=56)
        ac.glColor4f(1.0, 1.0, 1.0, 0.1) # Bar Backgrounds
        ac.glQuad(int(675 * scale), int(23 * scale), int(50 * scale), int(8 * scale))
        ac.glQuad(int(675 * scale), int(41 * scale), int(50 * scale), int(8 * scale))
        ac.glQuad(int(675 * scale), int(59 * scale), int(50 * scale), int(8 * scale))

        # Fill: Clutch (Blue)
        ac.glColor4f(0.0, 0.5, 1.0, 0.9)
        ac.glQuad(int(675 * scale), int(23 * scale), int(50 * clutchInput * scale), int(8 * scale))

        # Fill: Brake (Red)
        ac.glColor4f(1.0, 0.2, 0.2, 0.9)
        ac.glQuad(int(675 * scale), int(41 * scale), int(50 * brakeInput * scale), int(8 * scale))

        # Fill: Throttle (Green)
        ac.glColor4f(0.0, 1.0, 0.4, 0.9)
        ac.glQuad(int(675 * scale), int(59 * scale), int(50 * throttleInput * scale), int(8 * scale))

        # Names of Pedals
        # (Drawn using simple acLabels: Clutch, Brake, Throttle)
        # Note: We draw vertical KERS & WEAR bars below (y=75 to y=120)
        # Vertical Bar 1: KERS (x=635)
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(635 * scale), int(78 * scale), int(72 * scale), int(45 * scale)) # box background
        ac.glQuad(int(695 * scale), int(82 * scale), int(8 * scale), int(37 * scale)) # inner bar background
        ac.glColor4f(0.0, 0.94, 1.0, 0.9) # Cyan KERS Fill
        ac.glQuad(int(695 * scale), int(82 * scale + (37 * (1.0 - kersCharge)) * scale), int(8 * scale), int(37 * kersCharge * scale))

        # Vertical Bar 2: WEAR (x=712)
        ac.glColor4f(0.05, 0.05, 0.05, 0.9)
        ac.glQuad(int(712 * scale), int(78 * scale), int(72 * scale), int(45 * scale))
        ac.glQuad(int(768 * scale), int(82 * scale), int(8 * scale), int(37 * scale))
        ac.glColor4f(0.6, 0.6, 0.6, 0.9) # Grey Wear Fill (Note: Wear scales from 0 to 100%, we display remaining tire health)
        wear_left = max(0.0, min(1.0, 1.0 - tyreWear))
        ac.glQuad(int(768 * scale), int(82 * scale + (37 * (1.0 - wear_left)) * scale), int(8 * scale), int(37 * wear_left * scale))

        # ---------------------------------------------
        # SHIFT LIGHT BAR (Ganz oben, zentriert)
        # ---------------------------------------------
        if show_rpm and maxRpm > 0:
            pct = float(rpms) / float(maxRpm)
            if pct > 1.0:
                pct = 1.0

            total_segments = 24
            segment_gap = 2
            bar_w = 480 * scale
            segment_width = (bar_w - (segment_gap * scale * (total_segments - 1))) / total_segments
            active_segments = int(round(pct * total_segments))

            is_flashing = (pct >= 0.92) and (int(rpms * 0.1) % 2 == 0)

            # Center align bar
            start_x = (width * scale - bar_w) / 2.0

            for i in range(total_segments):
                x = start_x + (i * (segment_width + (segment_gap * scale)))
                
                # Default segment color: Background dark
                col = [0.15, 0.15, 0.15, 0.8]

                if is_flashing:
                    col = [1.0, 0.2, 0.2, 1.0] if (int(rpms * 0.1) % 2 == 0) else [0.0, 0.94, 1.0, 1.0]
                elif i < active_segments:
                    if i < total_segments * 0.6:
                        col = [0.0, 1.0, 0.4, 0.9] # Green
                    elif i < total_segments * 0.85:
                        col = [1.0, 1.0, 0.0, 0.9] # Yellow
                    else:
                        col = [1.0, 0.2, 0.2, 0.9] # Red

                ac.glColor4f(col[0], col[1], col[2], col[3])
                ac.glQuad(int(x), int(2 * scale), int(segment_width), int(12 * scale))
    except Exception as e:
        log_error("appGL crash:\n" + traceback.format_exc())

# Text label overlays for Pedal panel
lblPedalClutch = 0
lblPedalBrake = 0
lblPedalThrottle = 0
lblKersName = 0
lblWearName = 0

def acUpdate(deltaT):
    global gear, speed, rpms, fuel, tireTemps, tirePressures, maxRpm, scale
    global lblGear, lblSpeed, lblPressFL, lblPressFR, lblPressRL, lblPressRR, lblBrakeF, lblBrakeR, lblGForce
    global clutchInput, brakeInput, throttleInput, kersCharge, tyreWear, brakeTemps, gForceLat, gForceLon
    global lblPedalClutchVal, lblPedalBrakeVal, lblPedalThrottleVal
    global lblPedalClutch, lblPedalBrake, lblPedalThrottle, lblKersName, lblWearName

    # Generate pedal text labels once in update if not present
    try:
        if lblPedalClutch == 0:
            lblPedalClutch = ac.addLabel(appWindow, "Clutch")
            ac.setPosition(lblPedalClutch, int(635 * scale), int(20 * scale))
            ac.setFontSize(lblPedalClutch, int(8 * scale))

            lblPedalBrake = ac.addLabel(appWindow, "Brake")
            ac.setPosition(lblPedalBrake, int(635 * scale), int(38 * scale))
            ac.setFontSize(lblPedalBrake, int(8 * scale))

            lblPedalThrottle = ac.addLabel(appWindow, "Throt")
            ac.setPosition(lblPedalThrottle, int(635 * scale), int(56 * scale))
            ac.setFontSize(lblPedalThrottle, int(8 * scale))

            lblKersName = ac.addLabel(appWindow, "KERS")
            ac.setPosition(lblKersName, int(642 * scale), int(92 * scale))
            ac.setFontSize(lblKersName, int(9 * scale))

            lblWearName = ac.addLabel(appWindow, "WEAR")
            ac.setPosition(lblWearName, int(720 * scale), int(92 * scale))
            ac.setFontSize(lblWearName, int(9 * scale))
    except:
        pass

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

        # G-Forces
        g_vec = ac.getCarState(0, acsys.CS.AccG)
        if isinstance(g_vec, list) or isinstance(g_vec, tuple):
            gForceLat = g_vec[0]
            gForceLon = g_vec[2]
        ac.setText(lblGForce, "{0:.2f} / {1:.2f}".format(gForceLat, gForceLon))
    except Exception as e:
        log_error("Pedal/GForce update failed:\n" + traceback.format_exc())

    # 4. Update Shared Memory (SM) values
    if simInfo is not None:
        # RPM & MaxRPM
        try:
            rpms = simInfo.physics.rpms
            maxRpm = simInfo.static.maxRpm
        except Exception as e:
            log_error("RPM SM update failed:\n" + traceback.format_exc())

        # KERS & Wear
        try:
            kersCharge = simInfo.physics.ersDelivery
            # Average tire wear from the 4 wheels
            wear_sum = 0.0
            for i in range(4):
                wear_sum += simInfo.physics.tyreWear[i]
            tyreWear = wear_sum / 4.0
        except Exception as e:
            log_error("Kers/Wear SM update failed:\n" + traceback.format_exc())

        # Tires (Temps and Pressures)
        try:
            for i in range(4):
                tireTemps[i] = simInfo.physics.tyreCoreTemperature[i]
                tirePressures[i] = simInfo.physics.wheelsPressure[i]
            
            # Formatted exactly: Temp (top), Pressure delta (bottom)
            # Pressure delta compared to ideal 28.0 PSI
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
