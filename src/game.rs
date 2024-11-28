const INDEX_ERR: &str = "{func_name} could not find {object} at index {index}";
const MIN_DIST_ERR: &str = "{func_name} failed to {action} because it is too close to another {object}";

#[derive(Debug)]
pub enum ArtilleryError<'a> {
    IndexError(&'a str),
    DistanceError(&'a str),
}

#[derive(Debug)]
pub struct Coordinate {
    pub x: f32,
    pub y: f32
}

impl Coordinate {
    /// `distance` returns the distance between two coordinates as a float. Uses Pythagoras'
    /// Theorem.
    pub fn distance(&self, coord2:&Coordinate) -> f32 {
        ((self.x - coord2.x).powf(2.0) + (self.y - coord2.y).powf(2.0)).sqrt()
    }

    /// `contains` accepts a Coordinate, `coord2`, and a float, `radius`, and determines if they are
    /// *within range* of each other.
    /// 
    /// Order is unimportant, since our imaginary circle could be drawn from either point.
    ///
    /// Returns true if the Coordinates are bounded by a circle with one of the coordinates as
    /// the center.
    pub fn contains(&self, coord2:&Coordinate, radius:f32) -> bool {
        radius > self.distance(coord2)
    }
}

#[derive(Debug)]
pub struct Game {
     pub map_radius: f32,
     pub turn_time: u32,
     pub target_radius: f32,
     pub base_location: Coordinate,
     pub units: Vec<Coordinate>,
     pub destinations: Vec<Coordinate>,
     pub targets: Vec<Coordinate>,
}

/// This implementation is the full interface to interact with the Artillery game.
/// It contains all of the logic to interact with and run the game.
impl Game {
    /// `new` sets up the initial game state with these defaults:
    /// - `map_radius` = 100.0 -> The default map is 100 units wide
    /// - `turn_time` = 5000 -> The default number of cycles per turn is 5000
    /// - `target_radius` = 5.0 -> The default size of explosions is 5.0 units
    /// - `base_location` = 0,0 -> The default base location is the center of the map
    pub fn new() -> Game {
        Game {
            map_radius: 100.0, // Currently arbitrary
            turn_time: 5000, // Currently arbitrary
            target_radius: 5.0, // Currently arbitrary
            base_location: Coordinate {x:0.0, y:0.0}, // Currently arbitrary
            units: vec![],
            destinations: vec![],
            targets: vec![],
        }
    }

    /// `add_unit` accepts an `x` value and a `y` value as floats, and creates a unit at that location.
    ///
    /// Automatically populates `self.units` with the `Coordinate`s, and sets
    /// `self.destinations` to the same.
    ///
    /// Units that are not given a destination can be thought of as moving to the coordinate they
    /// started at.
    ///
    /// Returns `()`, or `ArtilleryError` on failure. Potential variants:
    /// - DistanceError -> A unit was placed too close to another.
    pub fn add_unit(&mut self, x:f32, y:f32) -> Result<(), ArtilleryError>{
        //NOTE: Need to incorporate minimum distances
        self.units.push(Coordinate {x, y});
        self.destinations.push(Coordinate {x, y});
        if true {Ok(())}
        else {Err(ArtilleryError::anceError(MIN_DIST_ERR))}
    }

    /// `remove_unit` accepts an `index` value, and removes the corresponding unit from the game.
    pub fn remove_unit(&mut self, index:usize) -> Result<(), ArtilleryError> {
        if let Some(unit) = self.units.get(index) {
            self.units.remove(index);
            self.destinations.remove(index);
            Ok(())
        }
        else {
            Err(ArtilleryError::IndexError("remove_unit could not find a unit at index={index}"))
        }
    }

//    /// `get_unit` accepts an `index` value, and returns the Coordinate for that unit.
//    pub fn get_unit(&self, index:usize) -> Result<&Coordinate, ArtilleryError> {
//    }

    /// `set_destination` accepts an `index`, `x`, and `y`, value, and updates the corresponding
    /// destination.
    ///
    /// *Destinations are never removed, they can only be reset.*
    pub fn set_destination(&mut self, index:usize, x:f32, y:f32) {
        self.destinations[index] = Coordinate {x:x, y:y};
    }

    /// `add_target` accepts an `x` value and `y` value as floats, and creates a target at that
    /// location.
    ///
    /// NOTE: must calculate a resource cost
    pub fn add_target(&mut self, x:f32, y:f32) {
        self.targets.push(Coordinate {x, y});
    }

    /// `remove_target` accepts an `index` value, and removes the corresponding target from the
    /// game.
    ///
    /// NOTE: must remove a resource cost
    pub fn remove_target(&mut self, index:usize) {
        self.targets.remove(index);
    }

    /// Returns a tuple of floats representing the x and x components of a unit's velocity.
    ///
    /// For every iteration of `turn_time`, these values are added/subtracted from a unit's x and y components to represent movement.
    ///
    /// These values are dependent on `self.turn_time`. Larger values for `turn_time` represent
    /// more steps/increments per turn, which results in smaller velocity components.
    fn calculate_velocity(&self, index:usize) -> (f32, f32) {
         let x_velocity = (self.destinations[index].x - self.units[index].x) / self.turn_time as f32;
         let y_velocity = (self.destinations[index].y - self.units[index].y) / self.turn_time as f32;
         (x_velocity, y_velocity)
    }

    /// `is_in_danger` accepts an index for a target (`target_index`) and an index for a unit
    /// (`unit_index`) and returns `true` if the unit is within the danger zone.
    fn is_in_danger(&self, target_index:usize, unit_index:usize) -> bool {
        let target_coords = &self.targets[target_index];
        let unit_coords = &self.units[unit_index];
        target_coords.contains(unit_coords, self.target_radius)
    }

    //fn calculate_radius(&self) -> f32 {

    //}

    //fn shot_cost(&self) -> f32 {

    //}

    /// Simulates a turn once all destinations / targets have been accepted. This function does not
    /// perform **any** validation. It is assumed that **all* input has been validated up to this
    /// point.
    ///
    /// Once the end conditions have been met (either no units, or a unit at the base) this method
    /// will signal that the game is over, and reset the game's state.
    ///
    /// `run_turn` performs the following tasks:
    /// 1. Calculate the velocities of all units
    /// 2. Calculate the timing of artillery fire. NOTE: requires algo for shot costs
    /// 3. Iterate over each milisecond set by `self.turn_time`. Each iteration:
    ///     1. Add velocity to each unit's coordinates to determine new position
    ///     2. If an explosion happens that milisecond, determine units in danger zones. If effected, the
    ///        unit is removed from the game using `remove_unit`
    /// 4. Determine if either player has won the game
    pub fn run_turn(&self) {
        // Calculate velocities:
        let mut velocities = vec![];
        for (index, _) in self.units.iter().enumerate() {
            velocities.push(self.calculate_velocity(index));
        }
    }
}

