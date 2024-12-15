#![allow(unused)]
mod game;

fn main() {
    // This will probably be broken into tests at some point.
    let mut test_game = game::Game::new();

    // Create a grid of units
    for x in 25..36 {
        for y in 25..36 {
            test_game.add_unit(x as f32, y as f32);
        }
    }
    println!("{test_game:?}");
    let code = test_game.run_turn();
    
    // Create
    println!("{code}");
    println!("{test_game:?}");
}
