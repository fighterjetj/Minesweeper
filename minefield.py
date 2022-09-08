import random, warnings, copy

# Passed coordinates are a tuple of (row, column) form


class Minefield:
    def __init__(self, height, width, num_mines):
        self.height = height
        self.width = width
        self.num_mines = num_mines
        # Generating the mines
        self.generate_mines()

    # Resets the data for flagged squares and adjacent mines
    def empty_lists(self):
        # Making an empty minefield
        self.adj_mines = [[]] * self.height
        for i in range(self.height):
            self.adj_mines[i] = [0] * self.width
        self.minefield = copy.deepcopy(self.adj_mines)
        self.flagged_squares = copy.deepcopy(self.adj_mines)

    def print_mines(self):
        print("Mine locations:")
        for row in self.minefield:
            print(row)

    def print_adj_mines(self):
        print("Number of adjacent mines (9 signifies a mine)")
        for row in self.adj_mines:
            print(row)

    def generate_mines(self):
        self.hidden_squares = set()
        self.mine_cords = set()
        self.flagged_squares_coordinates = set()
        self.empty_lists()
        # If there are more mines than spots in the minefield, raises exception
        if self.num_mines > self.width * self.height:
            raise (
                Exception(
                    "The number of mines to be generated is more than the number available"
                )
            )
        # If there are a lot of mines compared to the squares, the process may take some time
        elif self.num_mines > self.width * self.height / 2:
            warnings.warn(
                "The number of mines to be generated is more than half the number of available squares.  This may take a while."
            )
        for i in range(self.num_mines):
            # Getting a random coordinate in the minefield
            col = random.randrange(0, self.width)
            row = random.randrange(0, self.height)
            # Generates new coordinates until the coordinates do not overlap an existing mine
            while self.minefield[row][col] == 1:
                col = random.randrange(0, self.width)
                row = random.randrange(0, self.height)
            self.minefield[row][col] = 1
            # Impossible for there to be 9 adjacent mines so signifies the spot has a mine in it
            self.adj_mines[row][col] = 9
            self.mine_cords.add((row, col))
        # Generating the adjacent mine numbers
        for row in range(self.height):
            for col in range(self.width):
                self.hidden_squares.add((row, col))
                # Only need to calculate the number of adjacent mines for empty spots (0 is empty which is false)
                if not self.minefield[row][col]:
                    self.adj_mines[row][col] = self.gen_num_adjacent_mines((row, col))

    # Given a coordinate pair, get a list of coordinates of all adjacent mines
    def get_adj_mine_cords(self, cords):
        row = cords[0]
        col = cords[1]
        # Checking that a valid coordinate was passed
        if row < 0 or row >= self.height:
            raise (Exception("Invalid row passed"))
        elif col < 0 or col >= self.width:
            raise (Exception("Invalid column passed"))
        row_range = range(row - 1, row + 2)
        col_range = range(col - 1, col + 2)
        # Checking for being on the edge
        if row == 0:
            row_range = range(row, row + 2)
        elif row == self.height - 1:
            row_range = range(row - 1, row + 1)
        if col == 0:
            col_range = range(col, col + 2)
        elif col == self.width - 1:
            col_range = range(col - 1, col + 1)
        adj_cords = []
        # Iterating over the adjacent squares and appending them
        for curr_row in row_range:
            for curr_col in col_range:
                adj_cords.append((curr_row, curr_col))
        # Gets rid of the passed coordinate pair, as we only want adjacent coordinates
        adj_cords.remove((row, col))
        return adj_cords

    # Given a coordinate pair, returns a list of all adjacent squares with no adjacent mines
    def get_empty_adj(self, cords):
        empty_adj = []
        for cord in self.get_adj_mine_cords(cords):
            if self.has_no_adj_mines(cord):
                empty_adj.append(cord)
        return empty_adj

    # Given a coordinate pair, calculates the number of adjacent mines
    def gen_num_adjacent_mines(self, cords):
        row = cords[0]
        col = cords[1]
        num_adj = 0
        adj_cords = self.get_adj_mine_cords((row, col))
        for cord in adj_cords:
            curr_row = cord[0]
            curr_col = cord[1]
            # 1 is true and 0 is false
            if self.minefield[curr_row][curr_col]:
                num_adj += 1
        return num_adj

    # Given a coordinate pair, returns a list of tuples of the entire area that should be exposed
    # The way it works is it will reveal the entire area of squares with no adjacent mines, as well as any squares adjacent to those
    # Assumes the passed coordinates are empty
    def reveal_empty_area(self, cords):
        # Making a set to store empty coordinates - prevents duplicates
        empty_cords = set()
        empty_cords.add(cords)
        num_empty = 0
        # As long as new coordinates are getting added, the set will grow bigger
        # If the set doesn't grow bigger, then there are no new empty coordinates
        while num_empty != len(empty_cords):
            num_empty = len(empty_cords)
            new_empty = []
            for empty_cord in empty_cords:
                new_empty += self.get_empty_adj(empty_cord)
            empty_cords.update(new_empty)
        # Getting all coordinates adjacent to the empty squares and revealing them
        all_revealed = set()
        for cord in empty_cords:
            all_revealed.update(self.get_adj_mine_cords(cord))
        for cord in all_revealed:
            if not self.has_mine(cord):
                self.reveal_square(cord)

    # Code that reveals everything when a spot is clicked
    def click_spot(self, cords):
        # We only do things if the square has not been revealed yet
        if cords in self.hidden_squares:
            # If we click on a mine, we just return 0, otherwise we return 1
            if self.has_mine(cords):
                return 0
            # If there is at least one adjacent mine, we just reveal that mine
            if self.get_num_adj_mines(cords) != 0:
                self.reveal_square(cords)
            # If there are no adjacent mines, we reveal all directly connected squares with no adjacent mines
            else:
                self.reveal_empty_area(cords)
        return 1

    # Code that regenerates the minefield until the passed coordinates have no adjacent mines, raises an error if it takes a long time
    def make_spot_safe(self, cords):
        num_iters = 0
        while not self.has_no_adj_mines(cords):
            num_iters += 1
            self.generate_mines()
            if num_iters > 100:
                raise (
                    Exception(
                        "Tried to regenerate the minefield 100 times and failed each time.  Try reducing the number of mines"
                    )
                )

    # If the square is already flagged, unflags it, otherwise flags it
    def flag_square(self, cords):
        if self.is_flagged(cords):
            self.flagged_squares[cords[0]][cords[1]] = 0
            self.flagged_squares_coordinates.discard(cords)
        else:
            self.flagged_squares[cords[0]][cords[1]] = 1
            self.flagged_squares_coordinates.add(cords)

    def get_flagged_squares(self):
        return self.flagged_squares_coordinates

    def is_flagged(self, cords):
        return self.flagged_squares[cords[0]][cords[1]]

    def has_no_adj_mines(self, cords):
        return self.adj_mines[cords[0]][cords[1]] == 0

    def get_num_adj_mines(self, cords):
        return self.adj_mines[cords[0]][cords[1]]

    def has_mine(self, cords):
        return self.minefield[cords[0]][cords[1]]

    def reveal_square(self, cords):
        self.hidden_squares.discard(cords)
        self.flagged_squares_coordinates.discard(cords)

    def get_hidden_squares(self):
        return self.hidden_squares

    def get_mine_cords(self):
        return self.mine_cords
