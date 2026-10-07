import pymunk
import pymunk.pyglet_util
from pymunk.vec2d import Vec2d

import pyglet
from pyglet.window import key
from pyglet.math import Mat4
from pyglet import shapes

from character import Character


class Game:
    def __init__(self, input_sequence, timestep=0.1):
        # -------------------------
        # Scripted input
        # -------------------------
        self.input_sequence = input_sequence
        self.input_script = [
            (i * timestep, item)
            for i, item in enumerate(input_sequence)
        ]

        self.script_time = 0.0
        self.script_index = 0
        self.script_enabled = True

        # -------------------------
        # Game state
        # -------------------------
        self.distance_travelled = 0.0
        self.game_over = False
        self.paused = False
        self.debug_draw = False

        self.qDown = False
        self.wDown = False
        self.oDown = False
        self.pDown = False

        # -------------------------
        # Pyglet setup
        # -------------------------
        self.window = pyglet.window.Window()
        self.batch = pyglet.graphics.Batch()

        self.fps_display = pyglet.window.FPSDisplay(
            window=self.window
        )

        self.label = pyglet.text.Label(
            "0 meters",
            font_name="Times New Roman",
            font_size=24,
            x=self.window.width // 2,
            y=self.window.height * 0.9,
            anchor_x="center",
            anchor_y="center",
        )

        # -------------------------
        # Physics setup
        # -------------------------
        self.character = None
        self.space = self.setup_world()

        # Register Pyglet events
        self.window.push_handlers(
            on_draw=self.on_draw,
            on_key_press=self.on_key_press,
            on_key_release=self.on_key_release,
            on_close=self.on_close,
        )

    # ============================================================
    # Script control
    # ============================================================

    def set_script_keys(self, keys):
        keys = keys.upper()

        self.qDown = "Q" in keys
        self.wDown = "W" in keys
        self.oDown = "O" in keys
        self.pDown = "P" in keys

    def update_script(self, dt):
        if not self.script_enabled:
            return

        self.script_time += dt

        while (
            self.script_index < len(self.input_script)
            and self.script_time >= self.input_script[self.script_index][0]
        ):
            event_time, keys = self.input_script[self.script_index]

            self.set_script_keys(keys)

            print(f"t={event_time:.2f}: holding [{keys}]")

            self.script_index += 1

    def start_script(self):
        self.script_time = 0.0
        self.script_index = 0

        if self.input_script and self.input_script[0][0] == 0:
            keys = self.input_script[0][1]

            self.set_script_keys(keys)

            print(f"t=0.00: holding [{keys}]")

            self.script_index = 1

    # ============================================================
    # Main update
    # ============================================================

    def update(self, dt):
        if self.game_over:
            return

        self.update_script(dt)

        if self.qDown:
            self.character.move_thighL()

        if self.wDown:
            self.character.move_thighR()

        if self.oDown:
            self.character.move_calfL()

        if self.pDown:
            self.character.move_calfR()

        if not self.paused:
            self.step()

    # ============================================================
    # Keyboard events
    # ============================================================

    def on_key_release(self, symbol, modifiers):
        if symbol == key.Q:
            self.qDown = False

        elif symbol == key.W:
            self.wDown = False

        elif symbol == key.O:
            self.oDown = False

        elif symbol == key.P:
            self.pDown = False

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.end_game()

        elif symbol == key.R:
            self.character.reset()

        elif symbol == key.Q:
            self.qDown = True

        elif symbol == key.W:
            self.wDown = True

        elif symbol == key.O:
            self.oDown = True

        elif symbol == key.P:
            self.pDown = True

        elif symbol == key.S:
            self.step()

        elif symbol == key.SPACE:
            self.paused = not self.paused

        elif symbol == key.D:
            self.debug_draw = not self.debug_draw

    def on_close(self):
        self.end_game()

    # ============================================================
    # Physics
    # ============================================================

    def setup_world(self):
        space = pymunk.Space()

        space.gravity = (0, -9820)
        space.damping = 0.99

        space.on_collision(
            collision_type_a=100,
            collision_type_b=1,
            begin=self.hit_ground,
        )

        floor_height = 10

        floor = pymunk.Segment(
            space.static_body,
            Vec2d(-self.window.width * 100, floor_height),
            Vec2d(self.window.width * 100, floor_height),
            1,
        )

        floor.friction = 10.3
        floor.collision_type = 100

        space.add(floor)

        body_width = 100
        body_height = 200

        body_x = self.window.width // 2
        body_y = (
            floor_height
            + body_height
            + body_height / 8
            + 10
        )

        print("Body start:", body_x, body_y)

        self.character = Character(
            space,
            body_x,
            body_y,
            body_width,
            body_height,
        )

        return space

    def step(self):
        for _ in range(10):
            self.space.step(1 / 50 / 10 / 2)

    def hit_ground(self, arbiter, space, data):
        if self.game_over:
            return False

        self.game_over = True

        print("hit ground!")
        print("distance:", self.distance_travelled)

        self.end_game()

        return False

    # ============================================================
    # Drawing
    # ============================================================

    def draw_rect(self, h1, h2, c1, c2):
        w = self.window.width
        h = self.window.height

        lc = self.character.get_position()[0] - w // 2

        background = (
            (lc, h * h1),
            (w + lc, h * h1),
            (w + lc, h * h2),
            (lc, h * h2),
        )

        colors = (
            c1[0], c1[1], c1[2], c1[3],
            c1[0], c1[1], c1[2], c1[3],
            c2[0], c2[1], c2[2], c2[3],
            c2[0], c2[1], c2[2], c2[3],
        )

        obj = shapes.Polygon(
            *background,
            color=colors,
            batch=self.batch,
        )

        return [obj]

    def draw_white_line(self, h):
        objs = []

        objs += self.draw_rect(
            h,
            h + 0.01,
            (255, 255, 255, 255),
            (255, 255, 255, 100),
        )

        objs += self.draw_rect(
            h - 0.01,
            h,
            (255, 255, 255, 100),
            (255, 255, 255, 255),
        )

        return objs

    def draw_start(self):
        x = self.window.width / 2
        h = self.window.height

        w1 = 25
        w2 = 10

        line1 = (
            (x - w1, 10 / h),
            (x, 10 / h),
            (x, h * 0.28),
            (x - w2, h * 0.28),
        )

        line2 = (
            (x, 10 / h),
            (x + w1, 10 / h),
            (x + w2, h * 0.28),
            (x, h * 0.28),
        )

        color1 = (
            255, 255, 255, 50,
            255, 255, 255, 255,
            255, 255, 255, 255,
            255, 255, 255, 50,
        )

        color2 = (
            255, 255, 255, 255,
            255, 255, 255, 50,
            255, 255, 255, 50,
            255, 255, 255, 255,
        )

        return [
            shapes.Polygon(
                *line1,
                color=color1,
                batch=self.batch,
            ),
            shapes.Polygon(
                *line2,
                color=color2,
                batch=self.batch,
            ),
        ]

    def on_draw(self):
        self.window.clear()

        w = self.window.width
        h = self.window.height

        lc = self.character.get_position()[0] - w // 2

        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
        )

        self.window.projection = Mat4.orthogonal_projection(
            lc,
            lc + w,
            0,
            h,
            -1,
            1,
        )

        objs = []

        objs += self.draw_rect(
            0.5, 1.0,
            (0, 0, 255, 255),
            (0, 0, 50, 255),
        )

        objs += self.draw_rect(
            0.45, 0.5,
            (0, 200, 0, 255),
            (0, 0, 255, 255),
        )

        objs += self.draw_rect(
            0.45, 0.35,
            (0, 200, 0, 255),
            (0, 200, 0, 255),
        )

        objs += self.draw_rect(
            0.35, 0.25,
            (0, 200, 0, 255),
            (200, 0, 0, 255),
        )

        objs += self.draw_rect(
            10 / h,
            0.25,
            (200, 0, 0, 255),
            (200, 0, 0, 255),
        )

        objs += self.draw_white_line(0.1)
        objs += self.draw_white_line(0.2)
        objs += self.draw_white_line(0.25)
        objs += self.draw_white_line(0.28)
        objs += self.draw_start()

        self.batch.draw()

        if self.debug_draw:
            self.fps_display.draw()

            options = pymunk.pyglet_util.DrawOptions()
            self.space.debug_draw(options)

        else:
            self.character.draw()

        # Reset projection for UI
        self.window.projection = Mat4.orthogonal_projection(
            0,
            w,
            0,
            h,
            -1,
            1,
        )

        factor = 1.25 / 200

        self.distance_travelled = lc * factor

        self.label.text = (
            f"{self.distance_travelled:.1f} meters"
        )

        self.label.draw()

    # ============================================================
    # Game termination
    # ============================================================

    def end_game(self):
        pyglet.clock.unschedule(self.update)

        if not self.window.has_exit:
            self.window.close()

        pyglet.app.exit()

    # ============================================================
    # Run
    # ============================================================

    def run(self):
        self.print_commands()

        self.start_script()

        pyglet.clock.schedule_interval(
            self.update,
            0.01,
        )

        pyglet.app.run()

        return {
            "distance_travelled": self.distance_travelled,
            "game_over": self.game_over,
        }

    @staticmethod
    def print_commands():
        print("SPACE: Pause simulation")
        print("S: Step simulation")
        print("R: Reset character")
        print("D: Toggle debug draw of physics objects")
        print("Q: Apply force to left thigh")
        print("W: Apply force to right thigh")
        print("O: Apply force to left calf")
        print("P: Apply force to right calf")


if __name__ == "__main__":
    input_sequence = [
        "QO", "OP", "QWOP", "QP", "QWO", "WO",
        "OP", "WOP", "WP", "QWO", "QWP", "WO",
        "Q", "WO", "QWP", "WP", "QWOP", "QWO",
        "QWO", "", "WOP", "QW", "O", "OP",
    ]

    game = Game(input_sequence)

    results = game.run()

    print(results)
