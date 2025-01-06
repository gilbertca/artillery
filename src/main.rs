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
        game: Game
    ) -> impl Filter<Extract = (Game,), Error = std::convert::Infallible> + Clone {
        warp::any().map(move || game.clone())
    }
}

mod handlers {
    use crate::game::Game as _Game;
    use std::sync::Arc;
    use tokio::sync::Mutex;
    use warp::http::StatusCode;

    type Game = Arc<Mutex<_Game>>;

    pub async fn add_target(_game: Game, x: f32, y: f32) {
        match game.lock().await.add_target(x, y) {
            Ok => Ok(StatusCode::
        }
    }

}



