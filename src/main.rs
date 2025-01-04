use warp::Filter;
mod game;

#[tokio::main]
async fn main() {
}

mod filters {
    use super::handlers;
    use warp::Filter;
    use crate::game::Game as _Game;
    use std::sync::Arc;
    use tokio::sync::Mutex;

    // Making
    type Game = Arc<Mutex<_Game>>;
    
    /// `with_game` is used internally to include a thread-safe reference to the game's state
    fn with_game(
        game: Game
    ) -> impl Filter<Extract = (Game,), Error = std::convert::Infallible> + Clone {
        warp::any().map(move || game.clone())
    }
}

mod handlers {

}



