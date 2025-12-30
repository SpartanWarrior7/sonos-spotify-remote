import soco


TARGET_NAME = "Luke’s Room"

# 1) Find the speaker
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

# 2) Ask what action you want
print("")
print("Choose an action:")
print("1 = Play/Pause")
print("2 = Next track")
print("3 = Volume up")
print("4 = Volume down")

choice = input("Type 1, 2, 3, or 4 and press Enter: ").strip()

# 3) Do the action
if choice == "1":
    state = speaker.get_current_transport_info()["current_transport_state"]
    if state == "PLAYING":
        speaker.pause()
        print("Paused.")
    else:
        speaker.play()
        print("Playing.")

elif choice == "2":
    speaker.next()
    print("Skipped to next track.")

elif choice == "3":
    speaker.volume = min(speaker.volume + 5, 100)
    print("Volume is now:", speaker.volume)

elif choice == "4":
    speaker.volume = max(speaker.volume - 5, 0)
    print("Volume is now:", speaker.volume)

else:
    print("Invalid choice.")
