mod game;
mod handler;

// start MAIN
fn main() {
    let test_game = game::Game::new();
    println!("{test_game:?}");
}
// end MAIN
