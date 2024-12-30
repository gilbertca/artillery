use warp::Filter;
mod game;

#[tokio::main]
async fn main() {
    let game = Arc::new(Mutex::new(game::Game::new()));



    // Units
    warp::serve(get_targets).run(([127, 0, 0, 1], 8910)).await
}

mod warp_filters {
    use super::handlers;
    use std::sync::{Mutex, Arc};
    use crate::game;
    use warp::Filter;
    
//    // Target Endpoints
//    let targets_uri = warp::path("targets"); // /targets
//    let get_targets = targets_uri.and(warp::get()) // GET /targets
//        .map({
//            let game = game.clone();
//            move || {
//                warp::reply::json(&game
//                    .lock()
//                    .unwrap()
//                    .get_targets()
//                )
//            }
//        });

    fn with_game(
        game: 
    ) -> impl Filter<Extract = (Game,), Error = std::convert::Infallible> + Clone {
        warp::any().map(move || game.clone())
    }
}

mod warp_handlers {

}


