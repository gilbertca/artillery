#![allow(unused)]
mod game;

fn main() {
    let mut test_game = game::Game::new();
    test_game.add_unit(-100.0, 0.0);
    test_game.set_destination(0, -95.0, 0.0);
    test_game.add_target(-50.0, 0.0);
    println!("{test_game:?}");
    test_game.run_turn();
    println!("{test_game:?}");
    /// ADD ONE MORE TICK TO THE SIMULATION
    /// REMOVE TARGETS AND THEIR COSTS
}
