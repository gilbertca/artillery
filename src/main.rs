use std::collections::HashMap;
use warp::Filter;
use std::sync::Arc;
use tokio::sync::Mutex;

mod game;

#[tokio::main]
async fn main() {
    use game::Game;
    let mut game = Arc::new(Mutex::new(Game::new()));


}

mod filters {
    use warp::Filter;
    use crate::game::Game as _Game;
    use std::sync::Arc;
    use tokio::sync::Mutex;

    pub type Game = Arc<Mutex<_Game>>;

    
}

