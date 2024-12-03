// Error definitions begin
#[derive(Debug)]
pub enum ArtilleryError {
    IndexError(String),
    DistanceError(String),
}

impl ArtilleryError {
    pub fn index_error(func_name: &str, index: usize) -> ArtilleryError {
        let error_msg = format!("{func_name} failed to find an object at index: {index}").to_string();
        ArtilleryError::IndexError(error_msg)
    }

    pub fn maximum_distance_error(func_name: &str, action: &str, coord1: &Coordinate, coord2: &Coordinate) -> ArtilleryError {
        let error_msg = format!("{func_name} failed to {action}. {coord1:?} is too far from {coord2:?}.");
        ArtilleryError::DistanceError(error_msg)
    } 

}
// Error definitions END

// Coordinate definitions END
#[derive(Debug, Clone)]
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
// Coordinate definitions END

// Game definitions BEGIN
#[derive(Debug)]
pub struct Game {
     pub map_radius: f32,
     pub turn_time: usize,
     pub target_radius: f32,
     pub base_coords: Coordinate,
     pub max_unit_range: f32,
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
    /// - `base_coords` = 0,0 -> The default base location is the center of the map
    pub fn new() -> Game {
        Game {
            map_radius: 100.0, // Currently arbitrary
            turn_time: 5000, // Currently arbitrary
            target_radius: 5.0, // Currently arbitrary
            base_coords: Coordinate {x:0.0, y:0.0}, // Currently arbitrary
            max_unit_range: 2.0, // Currently arbitrary
            units: vec![],
            destinations: vec![],
            targets: vec![],
        }
    }

// adders BEGIN
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
        // NOTE: Do checks here.
        if false { return Err(ArtilleryError::index_error("ONLY HERE FOR COMPILER", 1)); }
        // All checks succeeded, push the coordinates:
        self.get_units().push(Coordinate {x, y});
        self.get_destinations().push(Coordinate {x, y});
        Ok(())
    }

    /// `add_target` accepts an `x` value and `y` value as floats, and creates a target at that
    /// location.
    ///
    /// NOTE: must calculate a resource cost
    pub fn add_target(&mut self, x:f32, y:f32) {
        self.targets.push(Coordinate {x, y});
    }
// adders END

// removers BEGIN
    /// `remove_unit` accepts an `index` value, and removes the corresponding unit from the game.
    ///
    /// Returns an `IndexError` if a unit does not exist.
    pub fn remove_unit(&mut self, index:usize) -> Result<(), ArtilleryError> {
        let units = self.get_units();
        match units.get(index) {
            None => Err(ArtilleryError::index_error("remove_unit", index)),
            Some(_) => {
                units.remove(index);
                self.get_destinations().remove(index);
                Ok(())
            }
        }
    }

    /// `remove_target` accepts an `index` value, and removes the corresponding target from the
    /// game.
    ///
    /// NOTE: must remove a resource cost
    pub fn remove_target(&mut self, index:usize) -> Result<(), ArtilleryError> {
        let targets = self.get_targets();
        match targets.get(index) {
            None => Err(ArtilleryError::index_error("remove_target", index)),
            Some(_) => {
                targets.remove(index);
                Ok(())
            }
        }
    }
// removers END

// getters BEGIN
    /// `get_unit` accepts an `index` value, and returns the Coordinate for that unit. This
    /// `Coordinate` represents a unit's current position.
    ///
    /// Returns an `IndexError` if a unit does not exist.
    pub fn get_unit(&mut self, index:usize) -> Result<&Coordinate, ArtilleryError> {
        match self.get_units().get(index) {
            None => Err(ArtilleryError::index_error("get_unit", index)),
            Some(unit) => Ok(unit)
        }
    }

    /// `get_units` returns a vector of coordinates. Each `Coordinate` represents a unit's current
    /// position.
    ///
    /// Should never fail. Useful if the underlying `Game` struct ever changes.
    pub fn get_units(&mut self) -> &mut Vec<Coordinate> {
        &mut self.units
    }

    /// `get_destination` accepts an `index` value, and returns a Coordinate for that unit. This
    /// `Coordinate` represents a unit's current destination.
    ///
    /// Returns an `IndexError` if a destination does not exist.
    pub fn get_destination(&mut self, index: usize) -> Result<&Coordinate, ArtilleryError> {
        match self.get_destinations().get(index) {
            None => Err(ArtilleryError::index_error("get_destination", index)),
            Some(unit) => Ok(unit)
        }
    }

    /// `get_destinations` returns a vector of coordinates. Each `Coordinate` represents a unit's current
    /// destination.
    ///
    /// Should never fail. Useful if the underlying `Game` struct ever changes.
    pub fn get_destinations(&mut self) -> &mut Vec<Coordinate> {
        &mut self.destinations
    }

    /// `get_target` accepts an `index` value, and returns a `Coordinate` for that target. This
    /// `Coordinate` represents an artillery target.
    ///
    /// Returns an `IndexError` if a target does not exist.
    pub fn get_target(&mut self, index:usize) -> Result<&Coordinate, ArtilleryError> {
        match self.get_targets().get(index) {
            None => Err(ArtilleryError::index_error("get_destination", index)),
            Some(target) => Ok(target)
        }
    }

    /// `get_targets` returns a vector of coordinates. Each `Coordinate` represents an
    /// artillery target.
    ///
    /// Should never fail. Useful if the underlying `Game` struct changes.
    pub fn get_targets(&mut self) -> &mut Vec<Coordinate> {
        &mut self.targets
    }

    /// `get_base_coords` returns a reference to a `Coordinate`. This `Coordinate` represents the
    /// location of the artillery player's base.
    ///
    /// Should never fail. Useful if the underlying `Game` struct changes.
    pub fn get_base_coords(&self) -> &Coordinate {
        &self.base_coords
    }

    /// `get_map_radius` returns the radius of the map.
    ///
    /// Should never fail. Useful if the underlying `Game` struct changes.
    pub fn get_map_radius(&self) -> f32 {
        self.map_radius
    }

    /// `get_max_unit_range` returns the range of units.
    ///
    /// Should never fail. Useful if the underlying `Game` struct changes.
    pub fn get_max_unit_range(&self) -> f32 {
        self.max_unit_range
    }

// getters END

// setters BEGIN
    /// `set_destination` accepts an `index`, `x`, and `y`, value, and updates the corresponding
    /// destination contained in `self.destinations`.
    ///
    /// *Destinations are never removed, they can only be reset.*
    pub fn set_destination(&mut self, index:usize, x:f32, y:f32) -> Result<(), ArtilleryError> {
        // Check if unit exists; return early if false
        if let Err(_) = self.get_unit(index) {
            return Err(ArtilleryError::index_error("set_destination", index));
        }

        // Check if Coordinate falls outside of map; return early if true
        let temp_coord = Coordinate {x:x, y:y};
        if temp_coord.distance(self.get_base_coords()) > self.get_map_radius() {
            return Err(ArtilleryError::maximum_distance_error("set_destination", "set a unit's destination outside of the map", &temp_coord, &self.base_coords));
        }

        // Check if Coordinate falls outside of units range; return early if true
        if temp_coord.distance(self.get_unit(index)?) > self.get_max_unit_range() {
            return Err(ArtilleryError::maximum_distance_error("set_destination", "set a unit's destination beyond their maximum range", &temp_coord, self.get_unit(index)?));
        }

        // Checks complete
        let destinations = self.get_destinations();
        destinations[index] = temp_coord;
        Ok(())
    }

    /// `set_position` accepts an `index`, `x`, and `y` value, and updates the corresponding position
    /// contained in `self.units`.
    ///
    /// NOTE: maybe later this will be abstracted to allow setting the position of *anything*, such
    /// as the base's position. Also, it could replace `set_destination` since we can accept a
    /// pointer to any vector which contains coordinates.
//    pub fn set_position(&mut self, index:usize, x:f32, y:f32) -> Result<(), ArtilleryError> {
//        // Check if unit exists; return early if false
//        let unit = match self.get_unit(index) {
//            Err(_) => return Err(ArtilleryError::index_error("set_position", index)),
//            Ok(unit) => unit,
//        };
//
//        // Check if Coordinate falls outside of map; return early if true
//        let temp_coord = Coordinate {x:x, y:y};
//        let base_coords = self.get_base_coords();
//        if temp_coord.distance(&base_coords) > self.get_map_radius() {
//            return Err(ArtilleryError::maximum_distance_error("set_destination", "set a unit's destination outside of the map", &temp_coord, &self.base_coords));
//        }
//
//        // Checks complete
//        let units = self.get_units();
//        units[index] = temp_coord;
//        Ok(())
//    }



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
// Game definitions END
