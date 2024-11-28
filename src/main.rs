#![allow(unused)]
mod game;

fn main() {
    let mut test_game = game::Game::new();
    // Debug
    println!("{test_game:?}");
    let value = test_game.add_unit(1.0, 1.0);
    println!("{value:?}");
    println!("{test_game:?}");
    test_game.set_destination(0, 2.0, 2.0);
    println!("{test_game:?}");
}
