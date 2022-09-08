import pygame, pygame.freetype, minefield, time

NUM_ROWS = 20
NUM_COLS = 30
NUM_MINES = 80
SQUARE_SIZE = 40
OUTER_BOUNDARY_WIDTH = 5
SQUARE_OUTLINE_WIDTH = 2
LINE_COLOR = (0, 0, 255)
MINE_COLOR = (255, 0, 0)
COVER_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (255, 255, 255)
FLAG_COLOR = MINE_COLOR
NUM_COLOR = LINE_COLOR
FONT = "Arial"
# The sleep time is how long the program waits after a flag(right click)
SLEEP_TIME = 0.2


class Minesweeper:
    # The square size is referring to the total square size, including the outline width
    # So if the square size is 20 and the square outline width is 2, the total blank space would be a 16 by 16 square
    # The outer boundary width refers to the width of the boundary around the entire window
    def __init__(
        self,
        num_rows=NUM_ROWS,
        num_cols=NUM_COLS,
        num_mines=NUM_MINES,
        square_size=SQUARE_SIZE,
        outer_width=OUTER_BOUNDARY_WIDTH,
        square_outline_width=SQUARE_OUTLINE_WIDTH,
        line_color=LINE_COLOR,
        mine_color=MINE_COLOR,
        flag_color=FLAG_COLOR,
        num_color=NUM_COLOR,
        cover_color=COVER_COLOR,
        first_click_safe=True,
        font=FONT,
        background_color=BACKGROUND_COLOR,
        sleep_time=SLEEP_TIME,
    ):
        # Initializing the instance variables
        self.minefield = minefield.Minefield(num_rows, num_cols, num_mines)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_mines = num_mines
        self.square_size = square_size
        self.outer_width = outer_width
        self.square_outline_width = square_outline_width
        self.line_color = line_color
        self.mine_color = mine_color
        self.first_click_safe = first_click_safe
        self.first_click = first_click_safe
        self.num_color = num_color
        self.cover_color = cover_color
        self.background_color = background_color
        self.sleep_time = sleep_time
        self.flag_color = flag_color
        # The total height is going to be the number of squares times the square width PLUS the top and bottom outer widths
        self.height = num_rows * square_size + 2 * outer_width
        self.width = num_cols * square_size + 2 * outer_width
        # By default the window is not open so it isn't running
        self.running = False
        # Initializing pygame
        pygame.init()
        pygame.freetype.init()
        self.font = pygame.freetype.SysFont(font, round(square_size / 2))
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Minesweeper")

    # Takes (row, column) coordinates and converts it to coordinates on the screen
    def row_col_to_cords(self, row_col):
        row = row_col[0]
        col = row_col[1]
        return (
            self.outer_width + self.square_size * col,
            self.outer_width + self.square_size * row,
        )

    # Takes screen coordinates and converts it to (row, column) coordinates
    # Coordinates on the outer edge will return 0
    def cords_to_row_col(self, cords):
        # Getting rid of the outer width offset and then dividing it by square size
        x = (cords[0] - self.outer_width) // self.square_size
        y = (cords[1] - self.outer_width) // self.square_size
        # Checking if coordinates are on the outer edge
        if x < 0 or x >= self.num_rows:
            return 0
        elif y < 0 or y >= self.num_cols:
            return 0
        return (y, x)

    # Draws the empty grid
    def draw_grid(self):
        # The outer outline
        pygame.draw.rect(
            self.screen,
            self.line_color,
            (0, 0, self.width, self.height),
            self.outer_width,
        )
        # Vertical lines
        for x in range(self.outer_width, self.width, self.square_size):
            pygame.draw.line(
                self.screen,
                self.line_color,
                (x, 0),
                (x, self.height),
                self.square_outline_width,
            )
        # Horizontal lines
        for y in range(self.outer_width, self.height, self.square_size):
            pygame.draw.line(
                self.screen,
                self.line_color,
                (0, y),
                (self.width, y),
                self.square_outline_width,
            )

    def draw_num_adj(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                # Offset for centering the number, because the number is half the size of the square
                offset = round(self.square_size / 3)
                cords = list(self.row_col_to_cords((row, col)))
                cords[0] += offset
                cords[1] += offset
                num_adj = self.minefield.get_num_adj_mines((row, col))
                # No number is drawn if no mines are adjacent
                if num_adj != 0:
                    self.font.render_to(
                        self.screen,
                        cords,
                        str(num_adj),
                        self.num_color,
                    )

    # Mines are just the other colored squares - should never be seen
    def draw_mines(self):
        for mine_cord in self.minefield.get_mine_cords():
            pygame.draw.rect(
                self.screen,
                self.mine_color,
                (mine_cord[0], mine_cord[1], self.square_size, self.square_size),
            )

    def draw_cover(self):
        for row_col in self.minefield.get_hidden_squares():
            cords = self.row_col_to_cords(row_col)
            pygame.draw.rect(
                self.screen,
                self.cover_color,
                (cords[0], cords[1], self.square_size, self.square_size),
            )

    # Flags are drawn as circles
    def draw_flags(self):
        for row_col in self.minefield.get_flagged_squares():
            cords = self.row_col_to_cords(row_col)
            # The radius is slightly smaller than half of the square's size
            radius = (self.square_size - self.square_outline_width * 2) // 2
            # The center must be offset a little to account for the outer edge
            circle_center = (
                cords[0] + self.square_outline_width // 2 + self.square_size // 2,
                cords[1] + self.square_outline_width // 2 + self.square_size // 2,
            )
            pygame.draw.circle(self.screen, self.flag_color, circle_center, radius)

    def lose_game(self):
        self.running = False

    # Function that handles mouse clicks
    def mouse_handler(self):
        mouseData = list(pygame.mouse.get_pressed())
        mouse_x, mouse_y = pygame.mouse.get_pos()
        row_col = self.cords_to_row_col((mouse_x, mouse_y))
        # Making sure not clicked on the edge
        if row_col:
            # If the mouse is left clicking, clicks that location
            if mouseData[0]:
                # Checking if this is a first click and if it should be safe
                if self.first_click:
                    self.first_click = False
                    self.minefield.make_spot_safe(row_col)
                    self.minefield.click_spot(row_col)
                elif self.minefield.is_flagged(row_col):
                    self.minefield.flag_square(row_col)
                elif not self.minefield.click_spot(row_col):
                    self.lose_game()
                time.sleep(self.sleep_time)
            # If the mouse is right clicking, flags the location
            elif mouseData[2]:
                self.minefield.flag_square(row_col)
                time.sleep(self.sleep_time)

    # Function that handles the passed key being pressed
    def key_handler(self, key):
        # Resets it all if r is pressed
        if key == pygame.K_r:
            self.minefield.generate_mines()
            self.first_click = self.first_click_safe

    def print_mine_info(self):
        self.minefield.print_mines()
        self.minefield.print_adj_mines()

    def render_window(self):
        # Checks if the window should be closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.key_handler(event.key)

        # Fills the background
        self.screen.fill(self.background_color)

        # Handles mouse input
        self.mouse_handler()

        # Draws everything
        self.draw_num_adj()
        self.draw_mines()
        self.draw_cover()
        self.draw_grid()
        self.draw_flags()

        # Updates the display
        pygame.display.update()

    def run_game(self):
        self.running = True
        while self.running:
            self.render_window()
