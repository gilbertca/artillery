use std::sync::Arc;
use tokio::sync::Mutex;

mod game;
type Game = Arc<Mutex<game::Game>>;

/// This is the entry point for hosting an Artillery Game server.
///
/// Running this will start a `warp` server on port 10707.
/// TODO: ArtilleryErrors are serializable, and can be included in `response` HashMaps
///
/// All paths either return or accept JSON objects.
/// URI paths:
/// - /units GET -> returns a list of all units' positions in a list
/// - /units/:index GET (index=usize) -> returns a single unit's position at `index`
/// - /units POST -> creates a unit at position `x`, `y`, from a json payload
/// - /units/:index DELETE (index=usize) -> deletes the unit at `index`
/// TODO: MISSING POSITION ENDPOINT
/// - /targets GET -> returns a list of all targets' positions in a list
/// - /targets:index GET (index=usize) -> returns a single target's position at `index`
/// - /targets POST -> creates a target at position `x`, `y`, from a json payload
/// - /targets DELETE -> deletes the newest target
/// - /game GET ->  returns the currently defined configuration for the game
/// - /game/run POST -> runs the simulation using `Game.run_turn`
/// TODO: both players must run the game, so the server needs to track the connections or name in
/// some way. perhaps all functions could simply accept a name to validate.
#[tokio::main]
async fn main() {
    use game::Game;
    use filters;

    let game = Arc::new(Mutex::new(Game::new()));

    let api = filters::all_filters(game);
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
            .or(set_destination(game.clone()))
            .or(get_all_targets(game.clone()))
            .or(get_target(game.clone()))
            .or(create_target(game.clone()))
            .or(delete_target(game.clone()))
            .or(get_game_config(game.clone()))
            .or(run_turn(game.clone()))
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

    /// POST /units/:index
    pub fn set_destination(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("units" / usize)
            .and(warp::post())
            .and(extract_coordinate_from_json())
            .and(with_game(game))
            .and_then(handlers::set_destination)
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
    
    /// POST /game/run
    pub fn run_turn(
        game: Game,
    ) -> impl Filter<Extract = (impl warp::Reply,), Error = warp::Rejection> + Clone {
        warp::path!("game" / "run")
            .and(warp::post())
            .and(with_game(game))
            // TODO: what values do we need to extract for running the turn?
            .and_then(handlers::run_turn)
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
    use crate::game::Coordinate;
    
    
    use warp::http::StatusCode;

    /// *   * **   * ***** ******* ******
    /// *   * * *  *   *      *    **
    /// *   * *  * *   *      *      **
    /// *   * *   **   *      *        **
    /// ***** *    * *****    *    ******
    
    /// `handlers::get_all_units` returns a list of all unit positions using `Game.get_units`
    /// Also includes all unit destinations using `Game.get_destinations`
    pub async fn get_all_units(game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        response.insert("positions",
                        serde_json::to_string(&&gamestate.get_units().clone()).unwrap());
        response.insert("destinations",
                        serde_json::to_string(&&gamestate.get_destinations().clone()).unwrap());

        Ok(warp::reply::json(&response))
    }

    /// `handlers::get_unit` returns a unit's position at `index` in the list using `Game.get_unit`
    /// Also includes the unit's destination using `Game.get_destination`
    pub async fn get_unit(index: usize, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.get_unit(index) {
            Ok(unit) => {
                response.insert("position",
                                serde_json::to_string(&unit.clone()).unwrap());
                response.insert("destination",
                    serde_json::to_string(&
                        gamestate
                        .get_destination(index)
                        .expect(format!("If a unit exists at {}, then a destination must exist at {}", index, index).as_str())
                        .clone()
                    ).unwrap(),
                );

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::OK));
            }
            Err(error) => {
                // `Game.get_unit` currently only fails when a unit doesn't exist at that index
                response.insert("error", serde_json::to_string(&error).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::NOT_FOUND));
            }
        }
    }

    /// `handlers::create_unit` creates a unit at the specified position using `Game.add_unit`
    /// There aren't any rules regarding unit limits; maybe that's the client's job
    pub async fn create_unit(coordinate: Coordinate, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.add_unit(coordinate.x, coordinate.y) {
            Ok(_) => {
                response.insert("coordinate",
                                serde_json::to_string(&coordinate.clone()).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::CREATED));
            },
            Err(error) => { // Currently only fails when unit is outside map, or inside the base
                response.insert("error", serde_json::to_string(&error).unwrap());

                Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::BAD_REQUEST))
            }
        }
    }

    /// `handlers::delete_unit` deletes a unit at the specified `index` using `Game.remove_unit`
    pub async fn delete_unit(index: usize, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.remove_unit(index) {
            Ok(_) => { return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::NO_CONTENT)); },
            Err(error) => { // `Game.remove_unit` currently only fails when index DNE
                response.insert("error", serde_json::to_string(&error).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::NOT_FOUND));
            }
        }
    }

    /// `handlers::set_destination` sets a unit's destination at a particular `index`
    pub async fn set_destination(index: usize, coordinate: Coordinate, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.set_destination(index, coordinate.x, coordinate.y) {
            Ok(_) => {
                response.insert("index", serde_json::to_string(&index).unwrap());
                response.insert("coordinate", serde_json::to_string(&coordinate).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::CREATED));
            }
            Err(error) => {
                response.insert("error", serde_json::to_string(&error).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::BAD_REQUEST));
            }
        }
    }


    /// *******  *     ***** ***** ***** ******* *******
    ///    *    * *    *   * *     *        *     **
    ///    *   *****   ****  * *** *****    *       **
    ///    *  *     *  *  ** *   * *        *         **
    ///    * *       * *   * ***** *****    *    *******

    /// `handlers::get_all_targets` returns list of target positions using `Game.get_targets`
    /// Also includes the current target costs using `Game.get_target_costs`
    pub async fn get_all_targets(game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        response.insert("targets", serde_json::to_string(&gamestate.get_targets().clone()).unwrap());
        response.insert("target_costs", serde_json::to_string(&gamestate.get_target_costs().clone()).unwrap());

        Ok(warp::reply::json(&response))
    }

    /// `handlers::get_target` returns a target's position at `index` in the list using
    /// `Game.get_target`
    pub async fn get_target(index: usize, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.get_target(index) {
            Ok(target) => {
                response.insert("target", serde_json::to_string(&target.clone()).unwrap());
                response.insert(
                    "target_cost",
                    serde_json::to_string(&
                            gamestate
                            .get_target_cost(index)
                            .expect(format!("If a target exists at {}, then a cost must exist at {}", index, index).as_str())
                            .clone()
                    ).unwrap()
                );

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::CREATED));
            }
            // `Game.get_target` currently only fails when the index DNE
            Err(error) => {
                response.insert("error", serde_json::to_string(&error).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::NOT_FOUND));
            }
        }
    }

    /// `handlers::create_target` creates a target at the specified position using
    /// `Game.add_target`
    pub async fn create_target(coordinate: Coordinate, game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.add_target(coordinate.x, coordinate.y) {
            Ok(_) => { 
                let coordinate = Coordinate { x: coordinate.x, y: coordinate.y };
                response.insert("target", serde_json::to_string(&coordinate).unwrap());
                let index = gamestate.get_targets().len() - 1;
                let target_cost = gamestate.get_target_cost(index).expect("Target was just created by `create_target`").clone();
                response.insert("cost", serde_json::to_string(&target_cost).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::CREATED));
            }
            Err(error) => { // Fails when target is out of map, and not enough resources
                response.insert("error", serde_json::to_string(&error).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::FORBIDDEN));
            },
        }
    }

    /// `handlers::delete_target` deletes the newest target using `Game.remove_newest_target`
    pub async fn delete_target(game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;
        let mut response: HashMap<&str, String> = HashMap::new();

        match gamestate.remove_newest_target() {
            Ok(_) => { return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::NO_CONTENT)); },
            Err(error) => {
                response.insert("error", serde_json::to_string(&error).unwrap());

                return Ok(warp::reply::with_status(warp::reply::json(&response), StatusCode::FORBIDDEN));
            }
        }

    }

    /// ****** ******* *    * ***** ***** *******
    /// *    *    *    *    * *     *   *  **    
    /// *    *    *    ****** ***** ****     **
    /// *    *    *    *    * *     *  **      **
    /// ******    *    *    * ***** *   * *******
    
    /// `handlers::get_game_config` returns all of 'settings' for the currently running `Game`
    pub async fn get_game_config(game: Game) -> Result<impl warp::Reply, Infallible> {
        let gamestate = game.lock().await;

        let mut response: HashMap<&str, String> = HashMap::new();
        response.insert("map_radius", serde_json::to_string(&gamestate.get_map_radius().clone()).unwrap());
        response.insert("target_radius", serde_json::to_string(&gamestate.get_target_radius().clone()).unwrap());
        response.insert("base_coords", serde_json::to_string(&gamestate.get_base_coords().clone()).unwrap());
        response.insert("base_radius", serde_json::to_string(&gamestate.get_base_radius().clone()).unwrap());
        response.insert("max_unit_range", serde_json::to_string(&gamestate.get_max_unit_range().clone()).unwrap());
        response.insert("max_resources", serde_json::to_string(&gamestate.get_max_resources().clone()).unwrap());
        response.insert("game_over", serde_json::to_string(&gamestate.get_game_over().clone()).unwrap());

        Ok(warp::reply::json(&response))
    }

    pub async fn run_turn(game: Game) -> Result<impl warp::Reply, Infallible> {
        let mut gamestate = game.lock().await;

        if let Ok(_) = gamestate.run_turn() {
            Ok(StatusCode::RESET_CONTENT)
        }
        else {
            panic!("`Game::run_turn` has returned an error to `handler::run_turn`");
        }

    }
}
