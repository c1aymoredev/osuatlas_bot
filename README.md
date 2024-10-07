# osuAtlas! IRC Bot

An IRC bot for osu! that provides various functionalities including performance point (PP) calculation, beatmap recommendations, and now playing (NP) handling.

## Features

- **PP Calculation**: Calculate PP for any beatmap with specified mods.
- **Beatmap Recommendations**: Get personalized beatmap recommendations based on your play style and preferences.
- **Now Playing Handling**: Automatically detect and process NP messages from osu! clients.
- **Mod Parsing**: Accurately parse and interpret osu! mods for calculations and recommendations.
- **Twitch stream notification**: The bot sends a notification when your favorite streamer starts broadcasting.
- **IRC Integration**: Seamlessly connect and interact with the osu! IRC server.

### Available Commands

- `!pp <beatmap_id> [mods]`: Calculate PP for the specified beatmap with optional mods.
- `!r [params]`: Get a beatmap recommendation based on your recent plays and specified tags (dt,hr,nm,aim,consistency,speed).
- `!with <mods>`: Recalculate PP for the last beatmap with new mods.
- `!notifyme <streamer_nickname>`: Subscribe to notifications about twitch broadcasts.

## Acknowledgements

- [osu!](https://osu.ppy.sh/) for the game and API
- [rosu-pp](https://github.com/MaxOhn/rosu-pp) for PP calculations
