import soco
from inputs import get_gamepad

TARGET_NAME = "Luke’s Room"

# Connect to Sonos speaker
speakers = soco.discover()
speaker = None
for s in speakers:
    if s.player_name == TARGET_NAME:
        speaker = s
        break

if speaker is None:
    print("Could not find speaker:", TARGET_NAME)
    raise SystemExit

print("Connected to:", speaker.player_name)
print("Listening for controller buttons... (Ctrl+C to stop)")
print("X (BTN_SOUTH) = Play/Pause toggle")
print("Circle (BTN_EAST) = Next track")
print("L1 (BTN_TL) = Volume up")
print("R1 (BTN_TR) = Volume down")

def toggle_play_pause():
    state = speaker.get_current_transport_info()["current_transport_state"]
    if state == "PLAYING":
        speaker.pause()
        print("Paused")
    else:
        speaker.play()
        print("Playing")

while True:
    events = get_gamepad()
    for event in events:
        # We only care about button presses (state == 1)
        if event.ev_type == "Key" and event.state == 1:
            if event.code == "BTN_SOUTH":
                toggle_play_pause()

            elif event.code == "BTN_EAST":
                speaker.next()
                print("Next track")

            elif event.code == "BTN_TL":
                speaker.volume = min(speaker.volume + 5, 100)
                print("Volume:", speaker.volume)

            elif event.code == "BTN_TR":
                speaker.volume = max(speaker.volume - 5, 0)
                print("Volume:", speaker.volume)
