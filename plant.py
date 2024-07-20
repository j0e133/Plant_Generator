import random
import numpy as np
import pygame

from typing import Callable, Any
from functools import partial, lru_cache
from dataclasses import dataclass
from queue import LifoQueue
from camera import Camera, vec2
from color import get_similar_color, Color
from l_system import LSystem, Rules



ColorGenerator = Callable[[], Color]



@dataclass(repr=False, slots=True, frozen=True)
class DrawSettings:
    angle: float
    trunk_segment_length: float
    trunk_width: float
    trunk_color_generator: ColorGenerator
    leaf_radius: float
    leaf_type: int
    leaf_color_generator: ColorGenerator

    @staticmethod
    def get_random() -> 'DrawSettings':
        trunk_r = random.randint(100, 250)
        trunk_g = random.randint(100, 250)
        trunk_b = random.randint(100, 250)

        leaf_r = random.randint(100, 250)
        leaf_g = random.randint(100, 250)
        leaf_b = random.randint(100, 250)

        return DrawSettings(
            angle = random.uniform(10, 20),
            trunk_segment_length = random.uniform(2.5, 4),
            trunk_width = random.uniform(2, 3),
            trunk_color_generator = lambda: get_similar_color(trunk_r, trunk_b, trunk_g),
            leaf_radius = random.uniform(2, 4),
            leaf_type = random.randint(0, 3),
            leaf_color_generator = lambda: get_similar_color(leaf_r, leaf_b, leaf_g)
        )



_LORAX_TREE_COLORS = ((250, 215, 5), (250, 175, 25), (250, 135, 175), (180, 125, 220))



class Plant(LSystem):
    __slots__ = ('draw_settings', 'length', 'render_funcs')

    # plant presets
    ASPEN_GROWTH_RULES: Rules = {'X': (('F[---X]+f-F[++++X]-X', 'F[+++X]-F+f[----X]+X'), (0.5, 0.5))}
    ASPEN_AXIOM = 'FX'
    ASPEN_DRAW_SETTINGS = DrawSettings(
        angle = 15.0,
        trunk_segment_length = 3.0,
        trunk_width = 2.0,
        trunk_color_generator = lambda: get_similar_color(195, 185, 175),
        leaf_radius = 3.0,
        leaf_type = 0,
        leaf_color_generator = lambda: get_similar_color(22, 180, 80),
    )

    LORAX_GROWTH_RULES: Rules = {'X': (('+xf+f+X', '-fxfX'), (0.5, 0.5))}
    LORAX_AXIOM = 'fF-F+f+F[ffX]--[ffX]--[ffX]--[ffX]--[ffX]--[ffX]--[ffX]--[ffX]--[ffX]'
    LORAX_DRAW_SETTINGS = DrawSettings(
        angle = 20.0,
        trunk_segment_length = 4.0,
        trunk_width = 2.0,
        trunk_color_generator = lambda: get_similar_color(195, 185, 175),
        leaf_radius = 5.0,
        leaf_type = 0,
        leaf_color_generator = lambda: get_similar_color(*random.choice(_LORAX_TREE_COLORS)),
    )

    FERN_GROWTH_RULES: Rules = {'X': 'F[+[X]++X][----X]Ff-X'}
    FERN_AXIOM = 'ffX'
    FERN_DRAW_SETTINGS = DrawSettings(
        angle = 15.0,
        trunk_segment_length = 3.0,
        trunk_width = 2.0,
        trunk_color_generator = lambda: get_similar_color(10, 187, 63),
        leaf_radius = 5.0,
        leaf_type = 3,
        leaf_color_generator = lambda: (0, 0, 0),
    )

    BUSH_GROWTH_RULES: Rules = {'X': (('fF[---FX]f[++F+X]FX', 'fF[++F+X]f[-F--X]FX'), (0.5, 0.5))}
    BUSH_AXIOM = '[--X][++X]'
    BUSH_DRAW_SETTINGS = DrawSettings(
        angle = 15.0,
        trunk_segment_length = 2.0,
        trunk_width = 2.0,
        trunk_color_generator = lambda: get_similar_color(88, 57, 39),
        leaf_radius = 3.0,
        leaf_type = 0,
        leaf_color_generator = lambda: get_similar_color(10, 137, 63),
    )

    SPOOKY_GROWTH_RULES: Rules = {'X': (('-F[---X]+F-ff[+++f+X]-X', '+F[+++X]-ff+F[-f---X]+fX'), (0.5, 0.5))}
    SPOOKY_AXIOM = 'FX'
    SPOOKY_DRAW_SETTINGS = DrawSettings(
        angle = 12.0,
        trunk_segment_length = 3.0,
        trunk_width = 2.0,
        trunk_color_generator = lambda: get_similar_color(88, 57, 39),
        leaf_radius = 0.0,
        leaf_type = 3,
        leaf_color_generator = lambda: (0, 0, 0),
    )


    def __init__(self, growth_rules: Rules, axiom: str, draw_settings: DrawSettings, length: float = 1.5) -> None: 
        super().__init__('FfXx[]+-', self.get_length_rule(length) | growth_rules, axiom)

        self.draw_settings = draw_settings

        self.length = length

        self.regrow()


    def regrow(self) -> None:
        self.reset()
        self.step(4)

        self.update_draw_settings(self.draw_settings)


    def get_mutation(self) -> 'Plant':
        rules = self.rules['X']

        if isinstance(rules, str):
            # mutate the branch
            new_rule = get_mutated_branch(rules)

            # 1/4 chance to mutate again
            if random.random() < 0.25:
                new_rule = get_mutated_branch(new_rule)

            new_length = random.uniform(max(0.5, self.length - 0.35), min(2.5, self.length + 0.35))

            new_plant = Plant(
                {'X': new_rule},
                self.axiom,
                self.draw_settings,
                new_length,
            )

            # return the new plant
            return new_plant

        else:
            old_branches = self.rules['X'][0]
            new_branches: list[str] = []

            for old_branch in old_branches:
                # mutate the branch
                new_branch = get_mutated_branch(old_branch)

                # 1/4 chance to mutate again
                if random.random() < 0.25:
                    new_branch = get_mutated_branch(new_branch)

                new_branches.append(new_branch)

            # compile new branches into a new plant
            new_probabilities = tuple(random.uniform(max(0.1, probability - 0.15), probability + 0.15) for probability in self.rules['X'][1]) # type: ignore

            new_length = random.uniform(max(0.5, self.length - 0.35), min(2.5, self.length + 0.35))

            new_plant = Plant(
                {'X': (tuple(new_branches), new_probabilities)},
                self.axiom,
                self.draw_settings,
                new_length,
            )

            # return the new plant
            return new_plant


    def update_draw_settings(self, draw_settings: DrawSettings) -> None:
        self.render_funcs: list[Callable[[pygame.Surface, Camera], None]] = []

        # instantiate state variables
        pos = (0.0, 0.0)
        angle = 90.0
        queue: LifoQueue[tuple[vec2, float]] = LifoQueue()

        f = 0

        self.state += ' '

        # generate draw functions
        for i in range(len(self.state) - 1):
            match self.state[i]:
                case 'F' | 'f': # move foward
                    f += 1

                    if self.state[i + 1] not in 'Ff':
                        new_pos = tuple(pos + angle_vector(angle) * (f * draw_settings.trunk_segment_length))

                        self.render_funcs.insert(0, partial(draw_trunk, start=pos, end=new_pos, width=int(draw_settings.trunk_width), color=draw_settings.trunk_color_generator()))

                        pos = new_pos

                        f = 0

                case 'X' | 'x': # draw leaf
                    self.render_funcs.append(partial(draw_leaf, leaf_type=draw_settings.leaf_type, center=pos, angle=angle, rad=draw_settings.leaf_radius, color=draw_settings.leaf_color_generator()))

                case '+': # turn left
                    angle += draw_settings.angle

                case '-': # turn right
                    angle -= draw_settings.angle

                case '[': # save state
                    queue.put((pos, angle))

                case ']': # restore state
                    pos, angle = queue.get()

        self.state = self.state[:-1]


    def render(self, surface: pygame.Surface, camera: Camera) -> None:
        for render_func in self.render_funcs:
            render_func(surface, camera)


    @staticmethod
    def get_length_rule(length: float) -> Rules:
        weights = [0.0, 0.0, 0.0, 0.0]

        # distribute weights
        a = int(length)
        b = a + 1

        weights[a] = b - length
        weights[b] = length - a

        # return new weights
        return {'F': (('F', 'Ff', 'FF', 'FfF'), tuple(weights))}


    @staticmethod
    def get_random_rules() -> Rules:
        length_rules = Plant.get_length_rule(random.uniform(1, 2))

        branch_rule_1 = 'F' + ''.join(random.choices((
            'F',
            'f',
            'fF',
            'Ff',
            'ff',
            '-F',
            '-f',
            '+F',
            '+f',
            '-',
            '-',
            '--',
            '---',
            '--f-',
            '--F-',
            '+',
            '+',
            '++',
            '+++',
            '++f+',
            '++F+',
            '[-fX]',
            '[-f-X]',
            '[+fX]',
            '[+f+X]',
            '[-fx]',
            '[-f-x]',
            '[+fx]',
            '[+f+x]',
        ), k=random.randint(10, 15)))

        for _ in range(random.randint(7, 10)):
            branch_rule_1 = get_mutated_branch(branch_rule_1)

        branch_rule_2 = branch_rule_1

        for _ in range(random.randint(2, 4)):
            branch_rule_2 = get_mutated_branch(branch_rule_2)

        growth_rules = {'X': ((branch_rule_1, branch_rule_2), (0.5, 0.5))}

        return length_rules | growth_rules



@lru_cache
def angle_vector(angle: float) -> np.ndarray[float, Any]:
    radians = np.radians(angle)
    return np.array((np.cos(radians), -np.sin(radians)), float)


def get_mutated_branch(branch: str) -> str:
    weights = [4, 4, 4, 4, 3, 3, 2, 3, 3, 2]

    # restrict mutation options to prevent errors
    chars = sum([(char in branch) * 2 ** i for i, char in enumerate('FfXx[]+-')])

    if not chars & 0b11000000:
        weights[0] = 0
        weights[1] = 0
    if not chars & 0b00000001:
        weights[2] = 0
    if not chars & 0b00000010:
        weights[3] = 0
        weights[4] = 0
    if not chars & 0b11000011:
        weights[5] = 0
    if not chars & 0b00000100:
        weights[6] = 0
    if not chars & 0b00001000:
        weights[7] = 0
    if not chars & 0b00010000:
        weights[8] = 0

    if branch.count('X') > 4:
        weights[5] = 0
        weights[7] = 0

    # select a mutation and get the mutated branch
    mutation = random.choices(range(len(weights)), weights)[0]

    match mutation:
        case 0: # add rotation
            i = get_random_character_index(branch, get_characters_in_string('+-', branch))
            return branch[:i] + branch[i] * random.randint(1, 2) + branch[i:]

        case 1: # remove rotation
            i = get_random_character_index(branch, get_characters_in_string('+-', branch))
            return branch[:i] + branch[i+1:]

        case 2: # lowercase 'F'
            return replace(branch, 'F', 'f')

        case 3: # uppercase 'f'
            return replace(branch, 'f', 'F')

        case 4: # remove 'f'
            i = get_random_character_index(branch, 'f')
            return branch[:i] + branch[i+1:]

        case 5: # add branch
            i = get_random_character_index(branch, get_characters_in_string('Ff+-', branch))
            return branch[:i] + get_random_branch() + branch[i:]

        case 6: # lowercase 'X'
            return replace(branch, 'X', 'x')

        case 7: # uppercase 'x'
            return replace(branch, 'x', 'X')

        case 8: # remove branch
            i, j = get_bracket_indexes(branch)
            return branch[:i] + branch[j+1:]

        case 9: # add 'f' or 'F'
            i = get_random_index(branch)
            return branch[:i] + random.choice(('F', 'f', 'f')) + branch[i:]

        case _: # ignore
            return branch


def replace(string: str, target: str, replacement: str) -> str:
    i = get_random_character_index(string, target)
    return string[:i] + replacement + string[i+1:]


def get_random_index(obj: str | list) -> int:
    return random.randint(0, len(obj) - 1)


def get_random_character_index(string: str, characters: str) -> int:
    for i in random.sample(range(len(string)), len(string)):
        if string[i] in characters:
            return i

    return -1


def get_bracket_indexes(string: str) -> tuple[int, int]:
    start_index = get_random_character_index(string, '[')
    index = start_index

    while True:
        if string[index] == '[':
            start_index = index

        if string[index] == ']':
            return start_index, index

        index += 1


def get_characters_in_string(character_set: str, string: str) -> str:
    return ''.join(filter(lambda x: x in string, character_set))


def get_random_rotation(max: int) -> str:
    return random.choice(('+', '-')) * random.randint(1, max)


def get_random_branch() -> str:
    rotation = get_random_rotation(4)

    if random.random() < 0.75:
        i = random.randint(1, len(rotation))

        rotation = rotation[:i] + 'F' + rotation[i:]

    branch = f'[{rotation}X]'

    return branch


def draw_trunk(surface: pygame.Surface, camera: Camera, start: vec2, end: vec2, width: int, color: Color) -> None:
    pygame.draw.line(surface, color, camera.transform(start), camera.transform(end), width)


def draw_leaf(surface: pygame.Surface, camera: Camera, leaf_type: int, center: vec2, angle: float, rad: float, color: Color) -> None:
    match leaf_type:
        case 0:
            pygame.draw.circle(surface, color, camera.transform(center), rad)
        case 1:
            for off in (-30, 0, 30):
                direction = angle_vector(angle + off) * rad
                pygame.draw.line(surface, color, camera.transform(tuple(center - direction)), camera.transform(tuple(center + direction * 3)), 1)
        case 2:
            direction = angle_vector(angle) * rad * 2
            right = (-direction[1], direction[0])
            pygame.draw.line(surface, color, camera.transform((center[0] + right[0], center[1] + right[1])), camera.transform((center[0] - right[0], center[1] - right[1])), int(rad))

