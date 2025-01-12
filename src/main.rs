use warp::Filter;
mod game;

#[tokio::main]
async fn main() {
}

mod filters {
    use super::handlers;
    use warp::Filter;

    
    /// `with_game` is used internally to include a thread-safe reference to the game's state
    fn with_game(
        game: handlers::Game
    ) -> impl Filter<Extract = (handlers::Game,), Error = std::convert::Infallible> + Clone {
        warp::any().map(move || game.clone())
    }
}

mod handlers {
    use crate::game::{Game as _Game, ArtilleryError};
    use std::sync::Arc;
    use tokio::sync::Mutex;
    use warp::http::StatusCode;

    pub type Game = Arc<Mutex<_Game>>;

    pub async fn add_target(game: Game, x: f32, y: f32) {

    }

}



