import soco
from inputs import get_gamepad
from soco.plugins.sharelink import ShareLinkPlugin


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

# Always control the group coordinator (important for playback + favorites)
speaker = speaker.group.coordinator
print("Controlling coordinator:", speaker.player_name)


print("Listening for controller buttons... (Ctrl+C to stop)")
print("X (BTN_SOUTH) = Play/Pause toggle")
print("Circle (BTN_EAST) = Next track")
print("L1 (BTN_TL) = Volume down")
print("R1 (BTN_TR) = Volume up")
print("Square (BTN_WEST) = Previous track")

def toggle_play_pause():
    state = speaker.get_current_transport_info()["current_transport_state"]
    if state == "PLAYING":
        speaker.pause()
        print("Paused")
    else:
        speaker.play()
        print("Playing")

# put this next part in but not sure what it does

def play_spotify_playlist_id(playlist_id: str):
    """
    Reliable way to start Spotify playlists on Sonos:
    use ShareLinkPlugin to queue from a Spotify share link.
    """
    plugin = ShareLinkPlugin(speaker)

    link = f"https://open.spotify.com/playlist/{playlist_id}"

    speaker.stop()
    # Force playback source to queue and reset it
    speaker.clear_queue()
    speaker.shuffle = True
    # This handles the Sonos-specific metadata/translation
    plugin.add_share_link_to_queue(link)

    speaker.play_from_queue(0)
    print(f"[spotify] Playing playlist via sharelink: {playlist_id}")


#not sure about part above


# Track last D-pad (HAT) state to prevent repeat firing
last_hat = {
    "ABS_HAT0X": 0,
    "ABS_HAT0Y": 0
}

PLAYLISTS = {
    "DOWN": "37i9dQZF1DX6R7QUWePReA",      # Christmas Classics
    "UP": "7xuYLV75BZdO351Eh37pyE",  # current liked playlist as of 12/23/2025
}


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
            
            elif event.code == "BTN_WEST":
                speaker.previous()
                print("Previous track")
            

            elif event.code == "BTN_TL":
                speaker.volume = max(speaker.volume - 5, 0)
                print("Volume:", speaker.volume)

            elif event.code == "BTN_TR":
                speaker.volume = min(speaker.volume + 5, 100)
                print("Volume:", speaker.volume)
             

        # --- D-pad (HAT) ---
        elif event.ev_type == "Absolute" and event.code in ("ABS_HAT0X", "ABS_HAT0Y"):
            # Debounce: only act when it CHANGES and is not center (0)
            if event.state != last_hat[event.code]:
                last_hat[event.code] = event.state

                if event.code == "ABS_HAT0Y":
                    if event.state == -1:
                        print("playing favorite playlist: Songs")                    
                        play_spotify_playlist_id(PLAYLISTS["UP"])
                       
                    elif event.state == 1:
                        print("playing favorite playlist: Christmas Classics")
                        play_spotify_playlist_id(PLAYLISTS["DOWN"])

                elif event.code == "ABS_HAT0X":
                    if event.state == -1:
                        print("D-pad LEFT")
                        # example action:
                        # speaker.previous()
                    elif event.state == 1:
                        print("D-pad RIGHT")
                        # example action:
                        # speaker.next()
"""        
        if event.ev_type == "Absolute":

            if event.code == "ABS_Z" and event.state > 30:
                speaker.volume = min(speaker.volume + 5, 100)

            elif event.code == "ABS_RZ" and event.state > 30:
                speaker.volume = max(speaker.volume - 5, 0)
"""

