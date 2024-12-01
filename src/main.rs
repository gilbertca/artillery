#![allow(unused)]
mod game;

fn main() {
    let mut test_game = game::Game::new();
    println!("{test_game:?}");
}
