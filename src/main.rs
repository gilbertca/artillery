use warp::Filter;
use std::sync::Arc;
use tokio::sync::Mutex;

mod game;
type Game = Arc<Mutex<game::Game>>;

/// This is the entry point for hosting an Artillery Game server.
///
/// Running this will start a `warp` server on port 10707.
///
/// All paths either return or accept JSON objects.
/// URI paths:
/// - /units GET -> returns a list of all units' positions in a list
/// - /units/:index GET (index=uszize) -> returns a single unit's position at **index**
/// - /units POST -> creates a unit at position `x`, `y`, from a json payload
/// - /units/:index DELETE (index=usize) -> deletes the unit at `index`
#[tokio::main]
async fn main() {
    use game::Game;
    use filters::all_filters;
    let mut game = Arc::new(Mutex::new(Game::new()));
    //game.lock().await.add_unit(10.0, 10.0);
    let api = all_filters(game);
    // Start server:
    warp::serve(api).run(([127, 0, 0, 1], 10707)).await;
}

mod filters {
    use warp::Filter;
    use crate::handlers;
    use crate::Game;
    use crate::game::Coordinate;


    /// All filters combined. 
    /// For a list of all filters, see the documentation for the `main` crate.
    pub fn all_filters(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        get_all_units(game.clone())
            .or(get_unit(game.clone()))
            .or(create_unit(game.clone()))
    }

    /// GET /units
    pub fn get_all_units(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("units")
            .and(warp::get())
            .and(with_game(game))
            .and_then(handlers::get_all_units)
    }

    /// GET /units/:index
    pub fn get_unit(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("units" / usize)
            .and(warp::get())
            .and(with_game(game))
            .and_then(handlers::get_unit)
    }

    /// POST /units
    pub fn create_unit(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("units")
            .and(warp::post())
            .and(extract_coordinate_from_json())
            .and(with_game(game))
            .and_then(handlers::create_unit)
    }

    /// DELETE /units/:index
    pub fn delete_unit(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("units" / usize)
            .and(warp::delete())
            .and(with_game(game))
            .and_then(handlers::delete_unit)
    }


    /// `with_game` is an internal filter which clones the gamestate
    /// for each operation on an endpoint.
    fn with_game(game: Game) -> impl Filter<Extract = (Game,), Error = std::convert::Infallible> + Clone {
        warp::any().map(move || game.clone())
    }

    /// `extract_coordinate_from_json` is an internal filter which parses requests as json payloads.
    fn extract_coordinate_from_json() -> impl Filter<Extract = (Coordinate,), Error = warp::Rejection> + Clone {
        warp::body::json()
    }
}

mod handlers {
    use std::convert::Infallible;
    use std::collections::HashMap;
    use crate::Game;
    use crate::game::{ArtilleryError, Coordinate};
    use warp::http::StatusCode;

    
    /// `handlers::get_all_units` returns a list of all unit positions
    pub async fn get_all_units(mut game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        // {"units": [Coordinate1, ...]}
        let mut response: HashMap<&str, Vec<Coordinate>> = HashMap::new();

        let units: Vec<Coordinate> = gamestate.get_units().clone();
        response.insert("units", units);
        Ok(warp::reply::json(&response))
    }

    /// `handlers::get_unit` returns a unit's position at `index` in the list
    pub async fn get_unit(index: usize, mut game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        // {"unit": [Coordinate,]
        let mut response: HashMap<&str, Vec<Coordinate>> = HashMap::new();
        // Although there is only a single coordinate, wrapping it with a vector pleases the
        // compiler since I didn't add support for None/null types.

        let unit = gamestate.get_unit(index);
        if let Ok(unit) = gamestate.get_unit(index) {
            response.insert("unit", vec![unit.clone()]);
        }
        else {
            response.insert("unit", vec![]);
        }
        Ok(warp::reply::json(&response))
    }

    /// `handlers::create_unit` creates a unit at the specified position
    /// There aren't any rules regarding unit limits; maybe that's the client's job
    pub async fn create_unit(coordinate: Coordinate, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.add_unit(coordinate.x, coordinate.y) {
            Ok(StatusCode::CREATED)
        }
        else { // Currently only fails when unit is outside map
            Ok(StatusCode::BAD_REQUEST)   
        }
    }

    /// `handlers::delete_unit` delets a unit at the specified `index`
    pub async fn delete_unit(index: usize, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.remove_unit(index) {
            Ok(StatusCode::NO_CONTENT)
        }
        else {
            Ok(StatusCode::NOT_FOUND)
        }
    }
}
