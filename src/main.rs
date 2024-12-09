#![allow(unused)]
mod game;

fn main() {
    let mut test_game = game::Game::new();
    test_game.add_unit(-5.0, 0.0);
    test_game.set_destination(0, -1.1, 0.0);
    test_game.add_target(-69.0, 0.0);
    test_game.add_target(-66.0, 0.0);
    test_game.add_target(-20.0, 0.0);
    println!("{test_game:?}");
    let code = test_game.run_turn();
    /// ADD ONE MORE TICK TO THE SIMULATION
    /// REMOVE TARGETS AND THEIR COSTS
    println!("{code}");
    println!("{test_game:?}");
}
