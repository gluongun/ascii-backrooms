
import os
import sys
import math
import time
import msvcrt
from typing import List, Tuple


MAP_WIDTH = 24
MAP_HEIGHT = 24
FOV = 60.0
MAX_DEPTH = 16.0
MOVE_SPEED = 4.0
ROTATION_SPEED = 3.5


DISTANCE_CHARS = [' ', '░', '▒', '▓', '≡', '≈', '⌇', '☒', '☐', '⬛', '█']



class Colors:
    RESET = '\033[0m'


    YELLOW_NEON = '\033[38;5;227m'
    YELLOW_WARM = '\033[38;5;221m'
    YELLOW_DIM = '\033[38;5;179m'
    YELLOW_DARK = '\033[38;5;136m'
    GREEN_YELLOW = '\033[38;5;191m'
    GREEN_OLIVE = '\033[38;5;148m'
    GREEN_MOLD = '\033[38;5;149m'
    GREEN_DEEP = '\033[38;5;58m'


    WALLPAPER = '\033[38;5;186m'
    CARPET_DIRTY = '\033[38;5;100m'
    FLOORING = '\033[38;5;101m'
    CEILING = '\033[38;5;229m'


    FLUORESCENT = '\033[38;5;227m'
    FLUORESCENT_DIM = '\033[38;5;221m'
    SHADOW = '\033[38;5;94m'
    DARK_CORNER = '\033[38;5;58m'


    MOLD = '\033[38;5;149m'
    STAIN = '\033[38;5;136m'
    CRACK = '\033[38;5;94m'


    BRIGHT = '\033[38;5;227m'
    MEDIUM = '\033[38;5;221m'
    DIM = '\033[38;5;179m'
    DARK = '\033[38;5;136m'

    @staticmethod
    def fade_to_shadow(brightness: float) -> str:
        if brightness > 0.8:
            return Colors.BRIGHT
        elif brightness > 0.6:
            return Colors.MEDIUM
        elif brightness > 0.4:
            return Colors.DIM
        elif brightness > 0.2:
            return Colors.DARK
        else:
            return Colors.DARK_CORNER



WALL_COLORS = {
    1: Colors.WALLPAPER,
    2: Colors.MOLD,
    3: Colors.STAIN,
    4: Colors.YELLOW_DIM,
    5: Colors.CRACK
}


WALL_TEXTURES = {
    1: ['▓', '▒', '░', '█', '▓'],
    2: ['#', '&', '%', '$', '#'],
    3: ['~', '≈', '⌇', '~', '≈'],
    4: ['░', '▒', '▓', '░', '▒'],
    5: ['=', '-', '~', '=', '-']
}


class GameMap:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.data = self.create_backrooms_map()

    def create_backrooms_map(self) -> List[List[int]]:
        m = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]


        for i in range(MAP_WIDTH):
            m[0][i] = 1
            m[MAP_HEIGHT - 1][i] = 1
            m[i][0] = 1
            m[i][MAP_WIDTH - 1] = 1

        #room1
        for i in range(4, 9):
            m[3][i] = 2
            m[7][i] = 2
        for i in range(3, 8):
            m[i][4] = 2
            m[i][8] = 2

        #wet room
        for i in range(10, 15):
            m[10][i] = 3
            m[14][i] = 3
        for i in range(10, 15):
            m[i][10] = 3
            m[i][14] = 3


        m[12][12] = 4
        m[12][13] = 4
        m[13][12] = 4
        m[13][13] = 4


        # for i in range(8, 17):
        #     m[8][i] = 5
        #     m[16][i] = 5


        m[18][18] = 1
        m[18][19] = 1
        m[19][18] = 1
        m[19][19] = 3



        return m

    def is_wall(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.data[y][x] > 0


class RayCaster:
    def __init__(self, game_map: GameMap):
        self.map = game_map
        self.player_x = 10.0
        self.player_y = 10.0
        self.player_angle = 45.0

    def cast_ray(self, angle: float) -> Tuple[float, int, int]:
        rad_angle = math.radians(angle)
        sin_a = math.sin(rad_angle)
        cos_a = math.cos(rad_angle)

        dir_x = cos_a
        dir_y = sin_a

        map_x = int(self.player_x)
        map_y = int(self.player_y)

        delta_dist_x = abs(1.0 / dir_x) if dir_x != 0 else 1e30
        delta_dist_y = abs(1.0 / dir_y) if dir_y != 0 else 1e30

        step_x = 1 if dir_x > 0 else -1
        step_y = 1 if dir_y > 0 else -1

        if dir_x < 0:
            side_dist_x = (self.player_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - self.player_x) * delta_dist_x

        if dir_y < 0:
            side_dist_y = (self.player_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - self.player_y) * delta_dist_y

        hit = False
        side = 0

        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if map_x < 0 or map_x >= self.map.width or map_y < 0 or map_y >= self.map.height:
                return MAX_DEPTH, 0, 0

            if self.map.data[map_y][map_x] > 0:
                hit = True

        if side == 0:
            distance = (map_x - self.player_x + (1 - step_x) / 2) / dir_x
        else:
            distance = (map_y - self.player_y + (1 - step_y) / 2) / dir_y

        wall_type = self.map.data[map_y][map_x]

        if side == 0:
            tex_offset = self.player_y + distance * dir_y
        else:
            tex_offset = self.player_x + distance * dir_x
        tex_offset -= int(tex_offset)

        return max(distance, 0.01), wall_type, int(tex_offset * 4)


class Game:
    def __init__(self):
        self.screen_width = 80
        self.screen_height = 24
        self.game_map = GameMap()
        self.raycaster = RayCaster(self.game_map)
        self.running = True
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.fluorescent_flicker = 0.0

        print('\033[?25l', end='')

        try:
            import shutil
            cols, rows = shutil.get_terminal_size()
            self.screen_width = max(40, min(cols - 2, 120))
            self.screen_height = max(20, min(rows - 5, 35))
        except:
            pass


        self.screen_width = max(40, self.screen_width)
        self.screen_height = max(20, self.screen_height)



    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def move_cursor_home(self):
        print('\033[H', end='')

    def get_input(self) -> bool:
        if msvcrt.kbhit():
            key = msvcrt.getch()

            if key == b'\xe0':
                key = msvcrt.getch()
                if key == b'H':
                    self.move_forward()
                elif key == b'P':
                    self.move_backward()
                elif key == b'K':
                    self.rotate_left()
                elif key == b'M':
                    self.rotate_right()
                return True

            if key == b'w' or key == b'W':
                self.move_forward()
            elif key == b's' or key == b'S':
                self.move_backward()
            elif key == b'a' or key == b'A':
                self.move_left()
            elif key == b'd' or key == b'D':
                self.move_right()
            elif key == b'q' or key == b'Q':
                self.rotate_left()
            elif key == b'e' or key == b'E':
                self.rotate_right()
            elif key == b'\x1b':
                return False

        return True

    def move_forward(self):
        rad = math.radians(self.raycaster.player_angle)
        new_x = self.raycaster.player_x + math.cos(rad) * MOVE_SPEED
        new_y = self.raycaster.player_y + math.sin(rad) * MOVE_SPEED
        self.try_move(new_x, new_y)

    def move_backward(self):
        rad = math.radians(self.raycaster.player_angle)
        new_x = self.raycaster.player_x - math.cos(rad) * MOVE_SPEED
        new_y = self.raycaster.player_y - math.sin(rad) * MOVE_SPEED
        self.try_move(new_x, new_y)

    def move_left(self):
        rad = math.radians(self.raycaster.player_angle + 90)
        new_x = self.raycaster.player_x + math.cos(rad) * MOVE_SPEED
        new_y = self.raycaster.player_y + math.sin(rad) * MOVE_SPEED
        self.try_move(new_x, new_y)

    def move_right(self):
        rad = math.radians(self.raycaster.player_angle - 90)
        new_x = self.raycaster.player_x + math.cos(rad) * MOVE_SPEED
        new_y = self.raycaster.player_y + math.sin(rad) * MOVE_SPEED
        self.try_move(new_x, new_y)

    def rotate_left(self):
        self.raycaster.player_angle = (self.raycaster.player_angle - ROTATION_SPEED) % 360

    def rotate_right(self):
        self.raycaster.player_angle = (self.raycaster.player_angle + ROTATION_SPEED) % 360

    def try_move(self, x: float, y: float):
        if 0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT:
            if not self.game_map.is_wall(int(x), int(y)):
                self.raycaster.player_x = x
                self.raycaster.player_y = y

    def render_frame(self):

        screen_rows = []

        flicker = math.sin(self.fluorescent_flicker) * 0.2 + 0.8
        self.fluorescent_flicker += 0.05


        ray_data = []
        start_angle = self.raycaster.player_angle - (FOV / 2)

        for ray in range(self.screen_width):
            angle = start_angle + (ray / self.screen_width) * FOV
            distance, wall_type, tex_offset = self.raycaster.cast_ray(angle)
            ray_data.append((distance, wall_type, tex_offset))


        for y in range(self.screen_height):
            row_chars = []


            mid_point = self.screen_height // 2

            for x in range(self.screen_width):
                distance, wall_type, tex_offset = ray_data[x]


                wall_height = int(self.screen_height / distance) if distance > 0 else 0
                wall_height = min(wall_height, self.screen_height)

                start_y = (self.screen_height - wall_height) // 2
                end_y = start_y + wall_height


                if y < start_y or y >= end_y:

                    if y < mid_point:
                        ceiling_bright = 1.0 - (y / mid_point) * 0.3
                        if ceiling_bright > 0.7:
                            row_chars.append(Colors.CEILING + ' ' + Colors.RESET)
                        else:
                            row_chars.append(Colors.YELLOW_DIM + ' ' + Colors.RESET)
                    else:

                        floor_bright = ((y - mid_point) / mid_point)
                        if floor_bright < 0.5:
                            row_chars.append(Colors.CARPET_DIRTY + ' ' + Colors.RESET)
                        else:
                            row_chars.append(Colors.FLOORING + ' ' + Colors.RESET)
                else:
                    # Wall
                    brightness = 1.0 - min(1.0, distance / MAX_DEPTH)
                    brightness *= flicker

                    tex_index = min(int(brightness * len(DISTANCE_CHARS) - 1), len(DISTANCE_CHARS) - 1)
                    texture = WALL_TEXTURES.get(wall_type, WALL_TEXTURES[1])
                    char = texture[tex_offset % len(texture)]

                    wall_color = WALL_COLORS.get(wall_type, Colors.YELLOW_WARM)

                    if brightness > 0.7:
                        row_chars.append(wall_color + char + Colors.RESET)
                    elif brightness > 0.4:
                        row_chars.append(Colors.YELLOW_DIM + char + Colors.RESET)
                    elif brightness > 0.2:
                        row_chars.append(Colors.YELLOW_DARK + char + Colors.RESET)
                    else:
                        row_chars.append(Colors.DARK_CORNER + char + Colors.RESET)

            screen_rows.append(''.join(row_chars))


        self.move_cursor_home()


        for row in screen_rows:
            print(row)


        
        hud = f"\033[2;0H"
        hud += f"{Colors.FLUORESCENT}┌─ BACKROOMS ──────────────────────────────────────────────{Colors.RESET}\n"
        hud += f"{Colors.YELLOW_DIM}WASD=Move  Q/E=Rotate  ESC=Exit{Colors.RESET}\n"
        hud += f"{Colors.DARK_CORNER}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}"
        print(hud, end='')

    def cleanup(self):
        print('\033[?25h', end='')
        print('\033[0m', end='')
        self.clear_screen()
        print(Colors.FLUORESCENT + """
        ╔══════════════════════════════════════════════╗
        ║  you escaped the backrooms... for now.      ║
        ╚══════════════════════════════════════════════╝
        """ + Colors.RESET)

    def run(self):
        self.clear_screen()
        print(Colors.FLUORESCENT + "╔══════════════════════════════════════════════╗")
        print(
            Colors.FLUORESCENT + "║  " + Colors.YELLOW_NEON + "WELCOME TO THE BACKROOMS" + Colors.FLUORESCENT + "            ║")
        print(
            Colors.FLUORESCENT + "║  " + Colors.YELLOW_DIM + "Press any key to enter..." + Colors.FLUORESCENT + "             ║")
        print(Colors.FLUORESCENT + "╚══════════════════════════════════════════════╝" + Colors.RESET)
        time.sleep(2)

        frame_time = 1.0 / 30

        while self.running:
            start_time = time.time()

            if not self.get_input():
                self.running = False
                break

            self.render_frame()

            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time

            elapsed = time.time() - start_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

        self.cleanup()


def main():
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nThanks for playing!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
