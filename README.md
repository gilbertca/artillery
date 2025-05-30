# artillery - Quick Setup
A simple 2-player game written in Rust.

To create the server, run `cargo run`, or compile with `cargo build --release` and run the executable.

# Introduction
This game began as a personal project to learn Rust. To ensure *separation of concerns*, I planned to split the program into three (3) logical components:
1. <sup>you lost</sup>**The Game** `game.rs` - Each game is represented by an instance of the `Game` struct. One player directs an army of units, while the other player targets the map with artillery strikes. Both players prepare their moves in advance without knowledge of the others' moves. Once both players have finalized their plans, both turn's are played simultaneously. Will you outsmart your opponent and overrun their base before they destroy your army? Or will you predict your opponent's movements and destroy them before they can reach you?

2. **The Server** `main.rs` - The implementation `Game` was designed from the beginning to work within a RESTful architecture. This allows us to completely decouple the backend from the frontend. As of (2025-05-21), these features are not yet implemented.~The server is implemented using the `warp` framework. Each server currently only supports a single game, and the server doesn't bother trying to authenticate or identify users - this a feature, not a bug - the **Client** is responsible for that.~

3. **The Client** - I have decided not to build or include a client in this package because ~I'm tired~ I wanted to share the learning! Do whatever you want. Build a real-time hyper-realistic 3D simulation, or chart all of the points by hand and play using `curl`. Ideally, you and your friends have clients which enforce the rules, but I won't be there to stop you if you don't. A complete list of endpoints can be found below.

# Setup
**Dependencies**:
- serde = { version = "1.0.217", features = ["derive"] }
- tokio = { version = "1", features = ["full"] }
- warp = "0.3"
