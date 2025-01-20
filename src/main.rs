use std::collections::HashMap;
use warp::Filter;
use std::sync::Arc;
use tokio::sync::Mutex;
use game::Game as _Game;

pub type Game = Arc<Mutex<Hashmap>>


#[tokio::main]
async fn main() {
    // TODO: Save / Load games?
    let mut games: HashMap<String, Game> = HashMap::new();

    let routes = filters::

}

mod filters {
    use super::handlers;
    use warp::Filter;

    
    fn with_game(
        game: handlers::Game
    ) -> impl Filter<Extract = (handlers::Game,), Error = std::convert::Infallible> + Clone {
        warp::any().map(move || game.clone())
    }
}

mod handlers {

    pub async fn add_target(game: Game, x: f32, y: f32) {

    }

}



