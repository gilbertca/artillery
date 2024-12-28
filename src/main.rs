use std::sync::Arc;
use tokio::sync::Mutex;
use warp::Filter;
mod game;

#[tokio::main]
async fn main() {
    let game = game::Game::new();

    // Targets
    let targets_uri = warp::path("targets"); // /targets
    let get_targets = targets_uri.and(warp::get())
        .and(warp::path::param::<usize>())
        .map(|index| {
            
        }); // /targets/<index> - -1 returns all targets

    // Units
    warp::serve(get_target).run(([127, 0, 0, 1], 8910)).await
}

