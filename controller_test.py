import soco
from inputs import get_gamepad
from soco.plugins.sharelink import ShareLinkPlugin

LUKE_NAME = "Luke’s Room"
DLK_NAME = "Dining/Living/Kitchen"
FAMILY_NAME = "Family Room"

PLAYLISTS = {
    "DOWN": "37i9dQZF1DX6R7QUWePReA",  # Christmas Classics
    "UP": "7xuYLV75BZdO351Eh37pyE",    # your playlist
}

def find_zone(name: str, zones):
    for z in zones:
        if z.player_name == name:
            return z
    raise SystemExit(f"Could not find speaker: {name}")

def ensure_solo(zone):
    """Make sure this zone is not joined to another group."""
    try:
        if zone.group.coordinator.uid != zone.uid:
            zone.unjoin()
    except Exception:
        try:
            zone.unjoin()
        except Exception:
            pass

def group_zones(coordinator, members):
    """Make coordinator solo, then join members to it."""
    ensure_solo(coordinator)
    for m in members:
        if m.uid == coordinator.uid:
            continue
        try:
            m.join(coordinator)
        except Exception:
            pass

def play_spotify_playlist_id(zone, playlist_id: str, shuffle: bool = True):
    """Queue playlist via Spotify share link on the zone's coordinator and play."""
    zone = zone.group.coordinator
    plugin = ShareLinkPlugin(zone)

    link = f"https://open.spotify.com/playlist/{playlist_id}"

    zone.stop()
    zone.clear_queue()
    plugin.add_share_link_to_queue(link)

    zone.shuffle = shuffle
    zone.play_from_queue(0)

    print(f"[spotify] Playing on '{zone.player_name}'")

# --- Discover zones once ---
zones = soco.discover()
if not zones:
    raise SystemExit("No Sonos speakers found")

luke = find_zone(LUKE_NAME, zones)
dlk = find_zone(DLK_NAME, zones)
family = find_zone(FAMILY_NAME, zones)

# Active target (where commands go)
active_zone = luke.group.coordinator

def set_target_luke():
    global active_zone
    ensure_solo(luke)
    active_zone = luke.group.coordinator
    print("Target set to: Luke’s Room")

def set_target_dlk_family():
    global active_zone
    group_zones(dlk, [family])
    active_zone = dlk.group.coordinator
    print("Target set to: Dining/Living/Kitchen + Family Room")

def toggle_play_pause():
    state = active_zone.get_current_transport_info()["current_transport_state"]
    if state == "PLAYING":
        active_zone.pause()
        print("Paused")
    else:
        active_zone.play()
        print("Playing")

print("Found zones:", luke.player_name, dlk.player_name, family.player_name)
print("Default target:", active_zone.player_name)
print("Listening for controller buttons... (Ctrl+C to stop)")
print("X (BTN_SOUTH) = Play/Pause toggle")
print("Circle (BTN_EAST) = Next track")
print("Square (BTN_WEST) = Previous track")
print("L1 (BTN_TL) = Volume down")
print("R1 (BTN_TR) = Volume up")
print("D-pad LEFT = target DLK+Family")
print("D-pad RIGHT = target Luke")
print("D-pad UP/DOWN = play playlists on current target")

# Debounce for D-pad
last_hat = {"ABS_HAT0X": 0, "ABS_HAT0Y": 0}

while True:
    for event in get_gamepad():

        # Buttons
        if event.ev_type == "Key" and event.state == 1:
            if event.code == "BTN_SOUTH":
                toggle_play_pause()

            elif event.code == "BTN_EAST":
                active_zone.next()
                print("Next track")

            elif event.code == "BTN_WEST":
                active_zone.previous()
                print("Previous track")

            elif event.code == "BTN_TL":
                active_zone.volume = max(active_zone.volume - 5, 0)
                print("Volume:", active_zone.volume)

            elif event.code == "BTN_TR":
                active_zone.volume = min(active_zone.volume + 5, 100)
                print("Volume:", active_zone.volume)

        # D-pad
        elif event.ev_type == "Absolute" and event.code in ("ABS_HAT0X", "ABS_HAT0Y"):
            if event.state != last_hat[event.code]:
                last_hat[event.code] = event.state

                # LEFT/RIGHT selects target
                if event.code == "ABS_HAT0X":
                    if event.state == -1:
                        set_target_dlk_family()
                    elif event.state == 1:
                        set_target_luke()

                # UP/DOWN plays on current target
                elif event.code == "ABS_HAT0Y":
                    if event.state == -1:
                        print(f"Play UP playlist on target: {active_zone.player_name}")
                        play_spotify_playlist_id(active_zone, PLAYLISTS["UP"])
                    elif event.state == 1:
                        print(f"Play DOWN playlist on target: {active_zone.player_name}")
                        play_spotify_playlist_id(active_zone, PLAYLISTS["DOWN"])
