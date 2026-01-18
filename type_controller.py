import soco
from soco.plugins.sharelink import ShareLinkPlugin

LUKE_NAME = "Luke’s Room"
DLK_NAME = "Dining/Living/Kitchen"
FAMILY_NAME = "Family Room"

PLAYLISTS = {
    "Christmas": "37i9dQZF1DX6R7QUWePReA",  # Christmas Classics
    "Liked": "7xuYLV75BZdO351Eh37pyE",    # your playlist
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
print("Choose an action:")
print("P = Play/Pause")
print("Next = Next track")
print("Up = Volume up")
print("Down = Volume down")
print("luke = set target luke")
print("family = set target dlk+family")
print("liked = set playlist liked songs")
print("christmas = set playlist christmas songs")
print("end = end loop")

while True:
    choice = input("Choose your option: ")
    if choice == "P":
        toggle_play_pause()
        
    elif choice == "Next":
        active_zone.next()
        
    elif choice =="Up":
        active_zone.volume = min(active_zone.volume + 5, 100)
        print("Volume:", active_zone.volume)
        
    elif choice =="Down":
        active_zone.volume = max(active_zone.volume - 5, 0)
        print("Volume:", active_zone.volume)
    
    elif choice == "luke":
        set_target_luke()
        
    elif choice =="family":   
        set_target_dlk_family()
        
    elif choice =="liked":    
        print(f"Play Liked playlist on target: {active_zone.player_name}")
        play_spotify_playlist_id(active_zone, PLAYLISTS["Liked"])
    
    elif choice =="christmas":  
        print(f"Play Christmas playlist on target: {active_zone.player_name}")
        play_spotify_playlist_id(active_zone, PLAYLISTS["Christmas"])
        
    elif choice == "end":
        print("ending loop")
        exit()
    else:
        print("Invalid Syntax, try again")
    