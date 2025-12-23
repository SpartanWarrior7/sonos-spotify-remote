import soco

TARGET_NAME = "Luke’s Room"

speakers = soco.discover()
speaker = None
for s in speakers:
    if s.player_name == TARGET_NAME:
        speaker = s
        break

if speaker is None:
    print("Could not find speaker:", TARGET_NAME)
    raise SystemExit

"""
# this plays/pauses music
 state = speaker.get_current_transport_info()["current_transport_state"]

print("Current state:", state)

if state == "PLAYING":
    print("Pausing music...")
    speaker.pause()
else:
    print("Playing music...")
    speaker.play()

print("Done.") """

# this next part skips current track
""" print("Skipping to next track...")
speaker.next()
print("Done.") """

#the next part increases volume by 5
current_volume = speaker.volume
print("Current volume:", current_volume)

new_volume = min(current_volume + 5, 100)
speaker.volume = new_volume

print("Volume increased to:", new_volume)



