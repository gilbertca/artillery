# artillery - Quick Setup
A simple 2-player game written in Rust.

To create the server, run `cargo run --release`, or compile with `cargo build --release` and run the executable. A complete list of endpoints can be found below.

To run the client, run `python artillery-client.py URL=[url]`, where `[url]` points to a running server. TODO: Implement argparse in the client

To create your own client, simply make RESTful requests to the address where your server is running. A full list of endpoints can be found below.

# Introduction
This game began as a personal project to learn Rust. To separate concerns, I split the program into three (3) logical components:
1. <sup>you lost</sup>**The Game** `game.rs` - Each game is represented by an instance of the `Game` struct. One player directs an army of units, while the other player targets the map with artillery strikes. Both players prepare their moves in advance without knowledge of the others' moves. Once both players have finalized their plans, both turns are played simultaneously. Will you outsmart your opponent and overrun their base before they destroy your army? Or will you predict your opponent's movements and destroy them before they can reach you?

2. **The Server** `main.rs` - The implementation `Game` was designed from the beginning to work within a RESTful architecture. This allows us to completely decouple the backend from the frontend. The server is implemented using the `warp` framework. Each server currently only supports a single game, and the server doesn't bother trying to authenticate or identify users.

3. **The Client** - `artillery-client.py` - For my own testing purposes, and for your own inspiration, I have included a simple client created with Python's implementation of `ncurses`. *The code in this client is NOT a perfect abstraction or perfect implementation. Use and/or enjoy at your own risk.*

# Endpoints
## GET
- `/units` - Returns a list of all `units` and their `destinations`
- `/units/[index=int]` - Returns a single `unit` based on its **index**
- `/targets` - Returns a list of all targets and their costs
- `/targets/[index=int]` - Returns a single target based on its **index**
- `/game` - Returns all of the configuration information for the game

## POST
- `/units` - {'x': float, 'y': float} Creates a unit at the provided x and y coordinates
- `/units/[index=int]` - {'x': float, 'y': float} Sets the destination of the unit at **index** to the provided x and y coordinates
- `/targets` - {'x': float, 'y': float} creates a unit at the provided x and y coordinates
- `/game/run` - Runs the simulation

## DELETE
- `/units/[index=int]` - Deletes the unit at the provided **index**
- `/targets` - Deletes the last created target

# Setup
**Rust Dependencies**:
- serde = { version = "1.0.217", features = ["derive"] }
- tokio = { version = "1", features = ["full"] }
- warp = "0.3" 

These entries should be located under `[dependencies]` in your **Cargo.toml** file. You can also use `cargo add` to add them manually, though you *may* run into issues if you use other versions.

**Python Dependencies**:
- certifi==2025.6.15
- charset-normalizer==3.4.2
- idna==3.10
- requests==2.32.4
- urllib3==2.4.0 

These entries are located in **requirements.txt**, and they can be installed with `pip install -r requirements.txt`. Your implementation of Python *probably* has the other dependencies in the standard library. If you are using a non-standard implementation and you are running into issues, ensure you have the `curses`, `time`, `json`, and `math` standard modules.

# TODOs
TODO: RUNNING THE SERVER FROM THE CMDLINE ON A SPECIFIED PORT / IP (CURRENTLY HARDCODED TO 127.0.0.1:10707)
TODO: argparse in the client
TODO: Creating endpoints for configuring the game's settings
TODO: Determine how to place units at the start - perhaps with a function, or predetermined setting - and implement it
