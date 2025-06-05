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
/// - /units/:index GET (index=usize) -> returns a single unit's position at `index`
/// - /units POST -> creates a unit at position `x`, `y`, from a json payload
/// - /units/:index DELETE (index=usize) -> deletes the unit at `index`
/// - /targets GET -> returns a list of all targets' positions in a list
/// - /targets:index GET (index=usize) -> returns a single target's position at `index`
/// - /targets POST -> creates a target at position `x`, `y`, from a json payload
/// - /targets DELETE -> deletes the newest target
/// - /game/settings GET ->  returns the currently defined configuration for the game
/// - /game/settings/ TODO: UPDATING GAME SETTINGS?
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
            .or(delete_unit(game.clone()))
            .or(get_all_targets(game.clone()))
            .or(get_target(game.clone()))
            .or(create_target(game.clone()))
            .or(delete_target(game.clone()))
            .or(get_game_config(game.clone()))
    }

    /// *   * **   * ***** ******* ******
    /// *   * * *  *   *      *    ** 
    /// *   * *  * *   *      *      **
    /// *   * *   **   *      *        **
    /// ***** *    * *****    *    ******

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

    /// *******  *     ***** ***** ***** ******* *******
    ///    *    * *    *   * *     *        *     **
    ///    *   *****   ****  * *** *****    *       **
    ///    *  *     *  *  ** *   * *        *         **
    ///    * *       * *   * ***** *****    *    *******

    /// GET /targets
    pub fn get_all_targets(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("targets")
            .and(warp::get())
            .and(with_game(game))
            .and_then(handlers::get_all_targets)
    }

    /// GET /targets/:index
    pub fn get_target(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("targets" / usize)
            .and(warp::get())
            .and(with_game(game))
            .and_then(handlers::get_target)
    }

    /// POST /targets
    pub fn create_target(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("targets")
            .and(warp::post())
            .and(extract_coordinate_from_json())
            .and(with_game(game))
            .and_then(handlers::create_target)
    }

    /// DELETE /targets
    pub fn delete_target(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("targets")
            .and(warp::delete())
            .and(with_game(game))
            .and_then(handlers::delete_target)
    }

    /// ****** ******* *    * ***** ***** *******
    /// *    *    *    *    * *     *   *  **    
    /// *    *    *    ****** ***** ****     **  
    /// *    *    *    *    * *     *  **      **
    /// ******    *    *    * ***** *   * *******

    /// GET /game
    pub fn get_game_config(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("game")
            .and(warp::get())
            .and(with_game(game))
            .and_then(handlers::get_game_config)
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
    use serde::Serialize;
    use crate::Game;
    use crate::game::{ArtilleryError, Coordinate};
    use warp::http::StatusCode;

    // This is required so that we may include different value types within our 'response' HashMaps
    #[derive(Serialize)]
    enum JSON {
        Coordinate(Coordinate),
        Coordinates(Vec<Coordinate>), // Vec<Coordinate> appears several times in `Game`'s config
        F32(f32),
        F32s(Vec<f32>), // This is so we can use the same enum for any function with a 'response'
        Usize(usize),
        Usizes(Vec<usize>), // This is so we can use the same enum for any function with a 'response' 
    }

    /// *   * **   * ***** ******* ******
    /// *   * * *  *   *      *    **
    /// *   * *  * *   *      *      **
    /// *   * *   **   *      *        **
    /// ***** *    * *****    *    ******
    
    /// `handlers::get_all_units` returns a list of all unit positions using `Game.get_units`
    /// Also includes all unit destinations using `Game.get_destinations`
    pub async fn get_all_units(mut game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        // {
        //  "positions": [Coordinate1, ...],
        //  "destinations": [Coordinate1, ...]
        // }
        let mut response: HashMap<&str, JSON> = HashMap::new();

        response.insert("positions",
                        JSON::Coordinates(gamestate.get_units().clone()));
        response.insert("destinations",
                        JSON::Coordinates(gamestate.get_destinations().clone()));
        Ok(warp::reply::json(&response))
    }

    /// `handlers::get_unit` returns a unit's position at `index` in the list using `Game.get_unit`
    /// Also includes the unit's destination using `Game.get_destination`
    pub async fn get_unit(index: usize, mut game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        // {
        //  "position": Coordinate1,
        //  "destination": Coordinate1
        // }
        let mut response: HashMap<&str, JSON> = HashMap::new();

        let unit = gamestate.get_unit(index);
        if let Ok(unit) = gamestate.get_unit(index) {
            response.insert("position",
                            JSON::Coordinate(unit.clone()));
            response.insert(
                "destination",
                JSON::Coordinate(
                    gamestate
                    .get_destination(index)
                    .expect(format!("If a unit exists at {}, then a destination must exist at {}", index, index).as_str())
                    .clone()
                ),
            );
        }
       Ok(warp::reply::json(&response))
    }

    /// `handlers::create_unit` creates a unit at the specified position using `Game.add_unit`
    /// There aren't any rules regarding unit limits; maybe that's the client's job
    pub async fn create_unit(coordinate: Coordinate, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.add_unit(coordinate.x, coordinate.y) {
            Ok(StatusCode::CREATED)
        }
        else { // Currently only fails when unit is outside map
               // TODO: OUGHT TO FAIL WHEN A UNIT IS PLACED ON THE BASE
            Ok(StatusCode::BAD_REQUEST)
        }
    }

    /// `handlers::delete_unit` deletes a unit at the specified `index` using `Game.remove_unit`
    pub async fn delete_unit(index: usize, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.remove_unit(index) {
            Ok(StatusCode::NO_CONTENT)
        }
        else {
            Ok(StatusCode::NOT_FOUND)
        }
    }

    /// *******  *     ***** ***** ***** ******* *******
    ///    *    * *    *   * *     *        *     **
    ///    *   *****   ****  * *** *****    *       **
    ///    *  *     *  *  ** *   * *        *         **
    ///    * *       * *   * ***** *****    *    *******

    /// `handlers::get_all_targets` returns list of target positions using `Game.get_targets`
    /// Also includes the current target costs using `Game.get_target_costs`
    pub async fn get_all_targets(mut game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        // {
        //  "targets": [Coordinate1, ...],
        //  "target_costs": [cost1, ...]
        // }
        let mut response: HashMap<&str, JSON> = HashMap::new();

        response.insert("targets", JSON::Coordinates(gamestate.get_targets().clone()));
        response.insert("target_costs", JSON::F32s(gamestate.get_target_costs().clone()));
        Ok(warp::reply::json(&response))
    }

    /// `handlers::get_target` returns a target's position at `index` in the list using
    /// `Game.get_target`
    pub async fn get_target(index: usize, mut game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        // {
        //  "target": Coordinate,
        //  "target_cost": cost1
        // }
        let mut response: HashMap<&str, JSON> = HashMap::new();

        let target = gamestate.get_target(index);
        if let Ok(target) = gamestate.get_target(index) {
            response.insert("target", JSON::Coordinate(target.clone()));
            response.insert(
                "target_cost",
                JSON::F32(
                        gamestate
                        .get_target_cost(index)
                        .expect(format!("If a target exists at {}, then a cost must exist at {}", index, index).as_str())
                        .clone()
                )
            );
        }
        Ok(warp::reply::json(&response))
    }

    /// `handlers::create_target` creates a target at the specified position using
    /// `Game.add_target`
    pub async fn create_target(coordinate: Coordinate, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.add_target(coordinate.x, coordinate.y) {
            Ok(StatusCode::CREATED)
        }
        // TODO: INTERPRET THE ARTILLERYERRORS
        else {
            Ok(StatusCode::BAD_REQUEST)   
        }
    }

    /// `handlers::delete_target` deletes the newest target using `Game.remove_newest_target`
    pub async fn delete_target(game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.remove_newest_target() {
            Ok(StatusCode::NO_CONTENT)
        }
        else {
            Ok(StatusCode::NOT_FOUND)
        }
    }

    /// ****** ******* *    * ***** ***** *******
    /// *    *    *    *    * *     *   *  **    
    /// *    *    *    ****** ***** ****     **
    /// *    *    *    *    * *     *  **      **
    /// ******    *    *    * ***** *   * *******
    
    /// `handlers::get_game_config` returns all of 'settings' for the currently running `Game`
    pub async fn get_game_config(game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        let mut response: HashMap<&str, JSON> = HashMap::new();
        response.insert("map_radius", JSON::F32(gamestate.get_map_radius().clone()));
        response.insert("target_radius", JSON::F32(gamestate.get_target_radius().clone()));
        response.insert("base_coords", JSON::Coordinate(gamestate.get_base_coords().clone()));
        response.insert("base_radius", JSON::F32(gamestate.get_base_radius().clone()));
        response.insert("max_unit_range", JSON::F32(gamestate.get_max_unit_range().clone()));
        response.insert("max_resources", JSON::F32(gamestate.get_max_resources().clone()));

        Ok(warp::reply::json(&response))
    }
}
