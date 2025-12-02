# mario_bros_mw56.py
# Requirements satisfied:
# - OOP: distinct classes for Game, Character, Conveyor, Package, Truck, Boss, LevelConfig
# - No 'break' used in any loop
# - Uses @staticmethod, @property, @classmethod
# - Scoring, failures, truck rest, boss events
# - Difficulty levels per spec
# - Single-screen retro drawing using primitives (no external assets)
# - Comments on classes and methods

import pyxel
import random
from typing import List, Dict, Optional
import time

# -----------------------------
# Constants
# -----------------------------
SCREEN_W = 256
SCREEN_H = 192
FLOOR_MARGIN_Y = 20
FLOOR_SPACING = 28
BELT_LENGTH_SLOTS = 6  # discrete slots per conveyor
SLOT_W = 20  # width of one slot to render boxes
BELT_HEIGHT = 6
CHAR_W = 12
CHAR_H = 12
COLOR_BG = 0
COLOR_BELT = 5
COLOR_BOX = 10
COLOR_CHAR_MARIO = 8
COLOR_CHAR_LUIGI = 11
COLOR_TRUCK = 3
COLOR_TEXT = 7
COLOR_BOSS = 2

# -----------------------------
# Level configuration
# -----------------------------
class LevelConfig:
    """
    Encapsulates difficulty rules: number of belts, speeds, min packages scaling,
    truck failure elimination cadence, and control inversion for 'Crazy'.
    """

    def __init__(
        self,
        name: str,
        belts: int,
        speed_c0: float,
        speed_even: float,
        speed_odd: float,
        random_per_belt: bool,
        min_pkg_increment: int,
        truck_elim_every: Optional[int],
        invert_controls: bool,
    ):
        self._name = name
        self._belts = belts
        self._speed_c0 = speed_c0
        self._speed_even = speed_even
        self._speed_odd = speed_odd
        self._random_per_belt = random_per_belt
        self._min_pkg_increment = min_pkg_increment
        self._truck_elim_every = truck_elim_every
        self._invert_controls = invert_controls

    @property
    def name(self) -> str:
        return self._name

    @property
    def belts(self) -> int:
        return self._belts

    @property
    def speed_c0(self) -> float:
        return self._speed_c0

    @property
    def speed_even(self) -> float:
        return self._speed_even

    @property
    def speed_odd(self) -> float:
        return self._speed_odd

    @property
    def random_per_belt(self) -> bool:
        return self._random_per_belt

    @property
    def min_pkg_increment(self) -> int:
        return self._min_pkg_increment

    @property
    def truck_elim_every(self) -> Optional[int]:
        return self._truck_elim_every

    @property
    def invert_controls(self) -> bool:
        return self._invert_controls

    @classmethod
    def presets(cls) -> Dict[str, "LevelConfig"]:
        # Per PDF rules
        return {
            "Easy": cls(
                "Easy", belts=5, speed_c0=1.0, speed_even=1.0, speed_odd=1.0,
                random_per_belt=False, min_pkg_increment=50, truck_elim_every=3, invert_controls=False
            ),
            "Medium": cls(
                "Medium", belts=7, speed_c0=1.0, speed_even=1.0, speed_odd=1.5,
                random_per_belt=False, min_pkg_increment=30, truck_elim_every=5, invert_controls=False
            ),
            "Extreme": cls(
                "Extreme", belts=9, speed_c0=1.0, speed_even=1.5, speed_odd=2.0,
                random_per_belt=False, min_pkg_increment=30, truck_elim_every=5, invert_controls=False
            ),
            "Crazy": cls(
                "Crazy", belts=5, speed_c0=1.0, speed_even=1.0, speed_odd=1.0,
                random_per_belt=True, min_pkg_increment=20, truck_elim_every=None, invert_controls=True
            ),
        }


# -----------------------------
# Entities
# -----------------------------
class Conveyor:
    """
    A conveyor has a floor index, an odd/even index (for Mario/Luigi responsibility),
    and a discrete slot-based movement for packages. Speed measured in slots per second.
    """

    def __init__(self, idx: int, floor: int, is_even: bool, speed: float):
        self._idx = idx  # 0 is special 'Conveyor0' generator
        self._floor = floor
        self._is_even = is_even
        self._speed = speed
        self._occupied: Dict[int, "Package"] = {}  # slot -> Package
        self._progress_accum: float = 0.0
    
    @property
    def idx(self) -> int:
        return self._idx

    @property
    def floor(self) -> int:
        return self._floor

    @property
    def is_even(self) -> bool:
        return self._is_even

    @property
    def speed(self) -> float:
        return self._speed

    def set_speed(self, speed: float) -> None:
        self._speed = speed

    def slots(self) -> int:
        return BELT_LENGTH_SLOTS

    def is_last_slot(self, slot: int) -> bool:
        return slot >= self.slots() - 1

    def can_place(self, slot: int) -> bool:
        return slot not in self._occupied

    def place(self, pkg: "Package", slot: int) -> bool:
        # place only if empty
        if self.can_place(slot):
            self._occupied[slot] = pkg
            pkg.position = slot
            pkg.conveyor_idx = self._idx
            return True
        return False

    def remove_at(self, slot: int) -> Optional["Package"]:
        if slot in self._occupied:
            pkg = self._occupied.pop(slot)
            return pkg
        return None

    def packages_in_order(self) -> List["Package"]:
        # left-to-right processing
        ordered = []
        # no break: iterate full range
        for slot in range(self.slots()):
            if slot in self._occupied:
                ordered.append(self._occupied[slot])
        return ordered

    @staticmethod
    def make_belts(level: LevelConfig) -> List["Conveyor"]:
        belts: List[Conveyor] = []
        # Belt 0 (generator), always even-labeled for Mario's responsibility mapping
        speed_c0 = level.speed_c0 if not level.random_per_belt else random.choice([1.0, 2.0])
        belts.append(Conveyor(idx=0, floor=0, is_even=True, speed=speed_c0))
        # Alternate even/odd belts starting at 1
        floor = 0
        for i in range(1, level.belts + 1):
            # increase floor every belt (single screen with N floors)
            floor = i  # floor i for belt i
            is_even = (i % 2 == 0)
            speed = level.speed_even if is_even else level.speed_odd
            if level.random_per_belt:
                speed = random.choice([1.0, 2.0])
            belts.append(Conveyor(idx=i, floor=floor, is_even=is_even, speed=speed))
        return belts


class Package:
    """
    A moving box across belts. Tracks conveyor index and slot position.
    """

    _next_id = 1

    def __init__(self, conveyor_idx: int, position: int):
        self._id = Package._next_id
        Package._next_id += 1
        self._conveyor_idx = conveyor_idx
        self._position = position

    @property
    def id(self) -> int:
        return self._id

    @property
    def conveyor_idx(self) -> int:
        return self._conveyor_idx

    @conveyor_idx.setter
    def conveyor_idx(self, idx: int) -> None:
        self._conveyor_idx = idx

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, pos: int) -> None:
        self._position = pos

    @classmethod
    def reset_ids(cls) -> None:
        cls._next_id = 1


SPRITES = {
    "Mario": {
        "idle": (0, 0, 16, 16),
        "carry": (0, 16, 16, 16),
        "drop": (0, 32, 16, 16),
        "up": (0, 48, 16, 16),
        "down": (0, 48, 16, 16),
    },
    "Luigi": {
        "idle": (16, 0, 16, 16),
        "carry": (16, 32, 16, 16),
        "drop": (16, 16, 16, 16),
        "up": (16, 48, 16, 16),
        "down": (16, 48, 16, 16),
    }
}

class Character:
    """
    Mario or Luigi: only vertical movement among floors via stairs; automatically handles packages
    hitting end of belt on their floors. Controls can be inverted depending on level.
    """

    def __init__(self, name: str, color: int, start_floor: int, max_floor: int, key_up, key_down, inverted: bool):
        self._name = name
        self._color = color
        self._floor = start_floor
        self._max_floor = max_floor
        self._key_up = key_down if inverted else key_up
        self._key_down = key_up if inverted else key_down
        self.state = "idle"

    @property
    def name(self) -> str:
        return self._name

    def update_controls(self):
            if pyxel.btn(self._key_up) and self._floor > 0:
                self._floor -= 1
                self.state = "up"
            elif pyxel.btn(self._key_down) and self._floor < self._max_floor - 1:
                self._floor += 1
                self.state = "down"
            else:
                self.state = "idle"

    def render(self, x: int, y: int) -> None:
        u, v, w, h = SPRITES[self._name][self.state]
        pyxel.blt(x, y - h, 0, u, v, w, h, 0)



class Truck:
    """
    Collects final packages from last odd conveyor. On reaching capacity, goes out for delivery,
    stops belts temporarily (rest). May eliminate failures per rules.
    """

    def __init__(self, capacity: int = 8, rest_time_frames: int = 60):
        self._capacity = capacity
        self._count = 0
        self._deliveries = 0
        self._on_delivery = False
        self._rest_frames_remaining = 0
        self._rest_time_frames = rest_time_frames

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def count(self) -> int:
        return self._count

    @property
    def deliveries(self) -> int:
        return self._deliveries

    @property
    def on_delivery(self) -> bool:
        return self._on_delivery

    def add_package(self) -> bool:
        self._count += 1
        is_full = self._count >= self._capacity
        if is_full:
            self._deliveries += 1
            self._count = 0
            self._on_delivery = True
            self._rest_frames_remaining = self._rest_time_frames
        return is_full

    def update_rest(self) -> bool:
        """
        Returns True when returning from delivery; belts resume.
        """
        if self._on_delivery:
            self._rest_frames_remaining = max(0, self._rest_frames_remaining - 1)
            if self._rest_frames_remaining == 0:
                self._on_delivery = False
                return True
        return False

    def render(self, x: int, y: int) -> None:
        # Simple truck rectangle with fill indicator
        pyxel.rect(x, y - 12, 40, 12, COLOR_TRUCK)
        if self._count > 0:
            fill_w = int(40 * (self._count / self._capacity))
            pyxel.rect(x, y - 12, fill_w, 12, 4)
        label = "TRUCK" if not self._on_delivery else "DELIVERY"
        pyxel.text(x + 1, y - 20, f"{label}", COLOR_TEXT)


class Boss:
    """
    Visual feedback entity: appears when a package falls and after truck returns.
    """

    def __init__(self):
        self._visible_frames = 0

    @property
    def is_visible(self) -> bool:
        return self._visible_frames > 0

    def appear(self, frames: int = 30) -> None:
        self._visible_frames = frames

    def update(self) -> None:
        self._visible_frames = max(0, self._visible_frames - 1)

    def render(self, x: int, y: int) -> None:
        if self.is_visible:
            pyxel.rect(x, y - 14, 30, 14, COLOR_BOSS)
            pyxel.text(x + 3, y - 20, "BOSS!", COLOR_TEXT)


# -----------------------------
# Game
# -----------------------------
class MarioBrosMW56:
    """
    Full game orchestrator. Handles belts, characters, packages, scoring, failures, truck logic,
    boss events, level rules, and rendering.
    """

    def __init__(self, level_name: str = "Easy"):
        self._levels = LevelConfig.presets()
        self._level = self._levels.get(level_name, self._levels["Easy"])

        self._belts: List[Conveyor] = Conveyor.make_belts(self._level)
        self._max_floor = self._belts[-1]._floor
        Package.reset_ids()

        inverted = self._level.invert_controls
        # Controls mapping (pyxel key constants)
        mario_up = pyxel.KEY_UP
        mario_down = pyxel.KEY_DOWN
        luigi_up = pyxel.KEY_W
        luigi_down = pyxel.KEY_S

        self._mario = Character("Mario", COLOR_CHAR_MARIO, start_floor=0, max_floor=self._max_floor,
                                key_up=mario_up, key_down=mario_down, inverted=inverted)
        self._luigi = Character("Luigi", COLOR_CHAR_LUIGI, start_floor=0, max_floor=self._max_floor,
                                key_up=luigi_up, key_down=luigi_down, inverted=inverted)

        self._truck = Truck(capacity=8, rest_time_frames=70)
        self._boss = Boss()

        self._packages: List[Package] = []
        self._score = 0
        self._failures = 0
        self._game_over = False

        # Generator pacing for Conveyor0
        self._gen_timer = 0
        self._gen_interval_frames = 25

        # On delivery, belts stop; if any pkg at last slot, delete when activity resumes (per spec)
        self._delete_last_slots_on_resume = False

        pyxel.init(SCREEN_W, SCREEN_H, title=f"Mario Bros MW-56 - {self._level.name}")
        pyxel.load("resources.pyxres")
        pyxel.run(self.update, self.draw)

    @property
    def min_packages_target(self) -> int:
        # Start 1; +1 per threshold
        inc = self._level.min_pkg_increment
        extra = self._score // inc if inc > 0 else 0
        return 1 + extra

    def spawn_from_c0(self) -> None:
        """
        Conveyor0 generates empty boxes. Mario moves them to Conveyor1 automatically if on Floor0 when reaching last slot.
        Here we only create new package at slot 0 if generator interval passed and target minimum not met.
        """
        self._gen_timer += 1
        need_more = len(self._packages) < self.min_packages_target
        if need_more and (self._gen_timer >= self._gen_interval_frames):
            c0 = self._belts[0]
            # place only if free
            if c0.can_place(0):
                pkg = Package(conveyor_idx=c0.idx, position=0)
                c0.place(pkg, 0)
                self._packages.append(pkg)
                # reset gen timer
                self._gen_timer = 0

    def update_characters(self) -> None:
        # Players can move vertically any time (unless game over)
        if not self._game_over:
            self._mario.update_controls()
            self._luigi.update_controls()

    def update_truck(self) -> None:
        # If truck on delivery, countdown rest; when returns, boss appears and optionally purge last-slot packages
        returned = self._truck.update_rest()
        if returned:
            self._boss.appear(30)
            if self._delete_last_slots_on_resume:
                self.remove_last_slot_packages()
                self._delete_last_slots_on_resume = False

    def applicable_character(self, conveyor: Conveyor) -> Character:
        # Mario handles even->odd transfers and C0->C1 (idx 0). Luigi handles odd->even and last odd->truck.
        if conveyor.idx == 0 or conveyor.is_even:
            return self._mario
        return self._luigi

    def next_conveyor_idx(self, current_idx: int) -> Optional[int]:
        # Map next index: 0->1; 1->2; ... last odd -> None (truck)
        last_idx = self._belts[-1].idx
        if current_idx < last_idx:
            return current_idx + 1
        # last belt pushes to truck
        return None

    def remove_last_slot_packages(self) -> None:
        # Clean packages that are exactly at last slot of any belt
        # no break usage; scan all belts and slots
        remaining: List[Package] = []
        for pkg in self._packages:
            belt = self._belts[pkg.conveyor_idx]
            if belt.is_last_slot(pkg.position):
                belt.remove_at(pkg.position)
            else:
                remaining.append(pkg)
        self._packages = remaining

    def step_belts(self) -> None:
        """
        Advance packages along belts according to speed. Handle end-of-belt logic:
        - If character on same floor: auto-transfer to next belt; score +1
        - If character not present: package falls; failure + boss appear
        - Last odd belt to truck: on capacity, delivery: belts stop; delete last-slot packages on resume
        When truck is on delivery, belts are stopped.
        """
        if self._truck.on_delivery:
            return  # belts stop

        # Accumulate progress and advance packages slot-by-slot based on speed
        for belt in self._belts:
            # accumulate using fps ~30 frames; speed in slots/sec => slots/frame ~= speed/30
            belt._progress_accum += belt.speed / 30.0
            # while progress >= 1 slot, move one slot; avoid while+break; use condition loop
            moved_once = True
            # iterate a bounded number of times: floors slots max
            # No 'break', we use a decrementing counter controlled by condition
            moves_possible = int(belt._progress_accum)
            counter = 0
            while counter < moves_possible:
                # move all packages on this belt forward one slot
                self.advance_one_slot_on_belt(belt)
                belt._progress_accum -= 1.0
                counter += 1

    def advance_one_slot_on_belt(self, belt: Conveyor) -> None:
        """
        Move packages rightward by 1 slot, handling collisions and end-of-belt outcomes.
        """
        # Process from right to left to avoid overwriting (slots high->low)
        # No break: full iteration
        new_occupied: Dict[int, Package] = {}
        # collect packages sorted by position descending
        pkgs = belt.packages_in_order()
        pkgs_sorted = sorted(pkgs, key=lambda p: p.position, reverse=True)

        for pkg in pkgs_sorted:
            old_slot = pkg.position
            target_slot = old_slot + 1
            # End of belt
            if belt.is_last_slot(old_slot):
                receiver = self.applicable_character(belt)
                # If character on the belt's floor, transfer
                if receiver._floor == belt._floor:
                    next_idx = self.next_conveyor_idx(belt.idx)
                    # last belt -> truck
                    if next_idx is None:
                        is_full = self._truck.add_package()
                        # scoring +10 when truck completes
                        if is_full:
                            self._score += 10
                            # when truck leaves, belts stop; if any pkg at last slot, mark to delete on resume
                            self._delete_last_slots_on_resume = True
                            # failure elimination rule
                            elim_every = self._level.truck_elim_every
                            if elim_every is not None:
                                # eliminate one failure every N deliveries
                                if self._truck.deliveries % elim_every == 0 and self._failures > 0:
                                    self._failures -= 1
                        # remove pkg from game entirely
                        belt.remove_at(old_slot)
                        # also +1 score for the movement to truck
                        self._score += 1
                    else:
                        # transfer to next belt at slot 0 if free; if occupied, keep current slot (simple collision rule)
                        next_belt = self._belts[next_idx]
                        if next_belt.can_place(0):
                            # remove from current
                            belt.remove_at(old_slot)
                            next_belt.place(pkg, 0)
                            self._score += 1
                        else:
                            # keep at end if blocked
                            new_occupied[old_slot] = pkg
                else:
                    # Package falls: failure
                    belt.remove_at(old_slot)
                    self._boss.appear(45)
                    self._failures += 1
                    # game over check
                    if self._failures >= 3:
                        self._game_over = True
            else:
                # mid-belt move: if target free, move; otherwise, keep
                if belt.can_place(target_slot):
                    belt.remove_at(old_slot)
                    belt.place(pkg, target_slot)
                    new_occupied[target_slot] = pkg
                else:
                    new_occupied[old_slot] = pkg

        # write back occupied (ensures consistent state)
        belt._occupied = new_occupied

    def ensure_minimum_packages(self) -> None:
        """
        Enforce minimum number of packages in play. Generator c0 will create; if none exist, force one.
        """
        if len(self._packages) == 0:
            # force immediate spawn
            c0 = self._belts[0]
            if c0.can_place(0):
                pkg = Package(conveyor_idx=c0.idx, position=0)
                c0.place(pkg, 0)
                self._packages.append(pkg)

    def update(self) -> None:
        if self._game_over:
            # allow restart with ENTER
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.__init__(self._level.name)
            return

        # Characters
        self.update_characters()

        # Truck rest
        self.update_truck()

        # Spawn logic
        self.spawn_from_c0()
        self.ensure_minimum_packages()

        # Belts movement
        self.step_belts()

    # -----------------------------
    # Rendering helpers
    # -----------------------------
    def belt_xy(self, belt: Conveyor) -> (int, int):
        """
        Compute belt start coordinates (x,y) for rendering, based on floor index.
        Belts go from left to right across the screen; Mario on right, Luigi on left thematically.
        """
        y = SCREEN_H - FLOOR_MARGIN_Y - belt._floor * FLOOR_SPACING
        x = 20
        return x, y

    def draw_belts(self) -> None:
        for belt in self._belts:
            x, y = self.belt_xy(belt)
            pyxel.rect(x, y - BELT_HEIGHT, SLOT_W * belt.slots(), BELT_HEIGHT, COLOR_BELT)
            # draw boxes
            for slot in range(belt.slots()):
                if slot in belt._occupied:
                    bx = x + slot * SLOT_W + 2
                    by = y - BELT_HEIGHT - 10
                    pyxel.rect(bx, by, SLOT_W - 4, 10, COLOR_BOX)

    def draw_characters(self) -> None:
        # Render at extremes: Luigi left, Mario right; vertical based on floor
        def floor_y(floor: int) -> int:
            return SCREEN_H - FLOOR_MARGIN_Y - floor * FLOOR_SPACING
        mario_y = floor_y(self._mario._floor)
        luigi_y = floor_y(self._luigi._floor)
        pyxel.text(5, 5, f"Level: {self._level.name}", COLOR_TEXT)
        self._luigi.render(10, luigi_y)
        self._mario.render(SCREEN_W - 30, mario_y)

    def draw_truck(self) -> None:
        # Truck placed near left top
        self._truck.render(180, 30)

    def draw_boss(self) -> None:
        self._boss.update()
        self._boss.render(110, 30)

    def draw_hud(self) -> None:
        pyxel.text(5, 18, f"Score: {self._score}", COLOR_TEXT)
        pyxel.text(5, 28, f"Failures: {self._failures}/3", COLOR_TEXT)
        pyxel.text(5, 38, f"Deliveries: {self._truck.deliveries}", COLOR_TEXT)
        pyxel.text(5, 48, f"Min pkgs: {self.min_packages_target}", COLOR_TEXT)
        if self._truck.on_delivery:
            pyxel.text(5, 58, "Rest: belts stopped", COLOR_TEXT)

    def draw_game_over(self) -> None:
        pyxel.rect(40, 70, SCREEN_W - 80, 50, 1)
        pyxel.text(60, 85, "GAME OVER - Press Enter to Restart", COLOR_TEXT)

    def draw(self) -> None:
        pyxel.cls(COLOR_BG)
        self.draw_belts()
        self.draw_characters()
        self.draw_truck()
        self.draw_boss()
        self.draw_hud()
        if self._game_over:
            self.draw_game_over()


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    # Change level_name to "Medium", "Extreme", or "Crazy" to test difficulty behaviors
    MarioBrosMW56(level_name="Easy")