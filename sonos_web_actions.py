import sys
import soco
from soco.plugins.sharelink import ShareLinkPlugin

LUKE_NAME = "Luke’s Room"
DLK_NAME = "Dining/Living/Kitchen"
FAMILY_NAME = "Family Room"

PLAYLISTS = {
    "Christmas": "37i9dQZF1DX6R7QUWePReA",  # Christmas Classics
    "Liked": "7xuYLV75BZdO351Eh37pyE",      # your playlist
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


def get_active_zone(target: str, luke, dlk, family):
    """
    Returns the coordinator zone to target based on a string:
      - "luke"
      - "dlk_family"
    """
    if target == "luke":
        ensure_solo(luke)
        return luke.group.coordinator

    if target == "dlk_family":
        group_zones(dlk, [family])
        return dlk.group.coordinator

    raise SystemExit(f"Unknown target: {target}")


def toggle_play_pause(active_zone):
    state = active_zone.get_current_transport_info().get("current_transport_state")
    if state == "PLAYING":
        active_zone.pause()
        print("Paused")
    else:
        active_zone.play()
        print("Playing")


def main():
    # Usage:
    #   python sonos_web_actions.py <action> [--target luke|dlk_family]
    #
    # Examples:
    #   python sonos_web_actions.py playpause --target luke
    #   python sonos_web_actions.py next --target dlk_family
    #   python sonos_web_actions.py volume_up --target luke
    #   python sonos_web_actions.py play_liked --target dlk_family

    if len(sys.argv) < 2:
        print("Usage: python sonos_web_actions.py <action> [--target luke|dlk_family]")
        sys.exit(1)

    action = sys.argv[1]
    target = "luke"  # default target

    if "--target" in sys.argv:
        i = sys.argv.index("--target")
        if i + 1 >= len(sys.argv):
            print("Error: --target requires a value (luke or dlk_family)")
            sys.exit(1)
        target = sys.argv[i + 1]

    zones = soco.discover()
    if not zones:
        raise SystemExit("No Sonos speakers found")

    luke = find_zone(LUKE_NAME, zones)
    dlk = find_zone(DLK_NAME, zones)
    family = find_zone(FAMILY_NAME, zones)

    active_zone = get_active_zone(target, luke, dlk, family)

    # --- Actions ---
    if action == "playpause":
        toggle_play_pause(active_zone)

    elif action == "next":
        active_zone.next()
        print("Next track")

    elif action == "volume_up":
        active_zone.volume = min(active_zone.volume + 5, 100)
        print("Volume:", active_zone.volume)

    elif action == "volume_down":
        active_zone.volume = max(active_zone.volume - 5, 0)
        print("Volume:", active_zone.volume)

    elif action == "play_liked":
        print(f"Play Liked playlist on target: {active_zone.player_name}")
        play_spotify_playlist_id(active_zone, PLAYLISTS["Liked"])

    elif action == "play_christmas":
        print(f"Play Christmas playlist on target: {active_zone.player_name}")
        play_spotify_playlist_id(active_zone, PLAYLISTS["Christmas"])

    else:
        raise SystemExit(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
