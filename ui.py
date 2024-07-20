import pygame

from typing import Callable
from event import EventManager
from plant import Plant
from camera import Camera



class Element:
    __slots__ = ('manager', '_listener_ids')

    def __init__(self, manager: 'UIManager') -> None:
        self.manager = manager

        self._listener_ids = []

    def listen(self, event_type: int, function: Callable[[pygame.Event], None]) -> None:
        self._listener_ids.append(self.manager.event_manager.add_listener(event_type, function))

    def remove(self) -> None:
        self.manager.event_manager.remove_listeners(*self._listener_ids)

    def render(self, screen: pygame.Surface) -> None: ...



class Text(Element):
    __slots__ = ('text', 'rect')

    def __init__(self, manager: 'UIManager', text: str, size: int, bold: bool, color: tuple[int, int, int], center: tuple[int, int]) -> None:
        super().__init__(manager)

        renderer = pygame.font.SysFont('Segoe UI', size, bold)

        self.text = renderer.render(text, True, color)

        self.rect = self.text.get_rect(center=center)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.text, self.rect)



class Interactable(Element):
    __slots__ = ('bounding_box', 'hovered', 'pressed')

    def __init__(self, manager: 'UIManager', bounding_box: pygame.Rect) -> None:
        super().__init__(manager)

        self.bounding_box = bounding_box

        self.hovered = False
        self.pressed = False

    def render(self, screen: pygame.Surface) -> None:
        if self.pressed:
            pygame.draw.rect(screen, (80, 80, 80), self.bounding_box)
        elif self.hovered:
            pygame.draw.rect(screen, (110, 110, 110), self.bounding_box)
        else:
            pygame.draw.rect(screen, (150, 150, 150), self.bounding_box)

    def _hover(self, event: pygame.Event) -> None:
        self.hovered = self.bounding_box.collidepoint(event.pos)

    def _press(self, event: pygame.Event) -> None:
        if event.button == pygame.BUTTON_LEFT and self.hovered:
            self.pressed = True

    def _release(self, event: pygame.Event) -> None:
        if self.pressed and event.button == pygame.BUTTON_LEFT:
            self.pressed = False



class Button(Interactable):
    __slots__ = ('function')

    def __init__(self, manager: 'UIManager', bounding_box: pygame.Rect, function: Callable) -> None:
        super().__init__(manager, bounding_box)

        self.function = function

        def release(event: pygame.Event) -> None:
            if self.pressed and event.button == pygame.BUTTON_LEFT:
                self.pressed = False

                if self.hovered:
                    self.function()

        self.listen(pygame.MOUSEMOTION, self._hover)
        self.listen(pygame.MOUSEBUTTONDOWN, self._press)
        self.listen(pygame.MOUSEBUTTONUP, release)


class MutationOption(Button):
    __slots__ = ('surface')

    IMAGE_W = 125
    IMAGE_H = 175
    IMAGE_SPACING = 5
    SURFACE_SIZE = (IMAGE_W * 3 + IMAGE_SPACING * 4, IMAGE_H * 2 + IMAGE_SPACING * 3)

    OFFSETS = (
        (IMAGE_SPACING,                   IMAGE_SPACING),
        (IMAGE_SPACING * 2 + IMAGE_W,     IMAGE_SPACING),
        (IMAGE_SPACING * 3 + IMAGE_W * 2, IMAGE_SPACING),
        (IMAGE_SPACING,                   IMAGE_SPACING * 2 + IMAGE_H),
        (IMAGE_SPACING * 2 + IMAGE_W,     IMAGE_SPACING * 2 + IMAGE_H),
        (IMAGE_SPACING * 3 + IMAGE_W * 2, IMAGE_SPACING * 2 + IMAGE_H),
    )

    def __init__(self, manager: 'UIManager', bounding_box: pygame.Rect, function: Callable, plant: Plant) -> None:
        super().__init__(manager, bounding_box, function)

        self.surface = pygame.Surface(self.SURFACE_SIZE)

        self.surface.fill(1)
        self.surface.set_colorkey(1)

        camera = Camera((self.IMAGE_W * 0.5, self.IMAGE_H - 10))

        for offset in self.OFFSETS:
            surf = pygame.Surface((self.IMAGE_W, self.IMAGE_H))
            surf.fill(0)

            plant.regrow()
            plant.render(surf, camera)

            self.surface.blit(surf, offset)

    def render(self, screen: pygame.Surface) -> None:
        super().render(screen)

        screen.blit(self.surface, self.bounding_box)



class MutationWindow(Element):
    __slots__ = ('options')

    SURFACE_SPACING = 25

    OFFSETS = (
        (50,                                                            190),
        (50 + MutationOption.SURFACE_SIZE[0] + SURFACE_SPACING,         190),
        (50 + MutationOption.SURFACE_SIZE[0] * 2 + SURFACE_SPACING * 2, 190),
        (50,                                                            190 + MutationOption.SURFACE_SIZE[1] + SURFACE_SPACING),
        (50 + MutationOption.SURFACE_SIZE[0] + SURFACE_SPACING,         190 + MutationOption.SURFACE_SIZE[1] + SURFACE_SPACING),
        (50 + MutationOption.SURFACE_SIZE[0] * 2 + SURFACE_SPACING * 2, 190 + MutationOption.SURFACE_SIZE[1] + SURFACE_SPACING),
    )

    def __init__(self, manager: 'UIManager', plant: Plant) -> None:
        super().__init__(manager)

        self.options = []

        self.pick(plant)

    def pick(self, option: Plant) -> None:
        self.manager.remove_elements(*self.options)

        plants = [option] + [option.get_mutation() for _ in range(5)]

        self.options = [
            MutationOption(
                self.manager,
                pygame.Rect(offset, MutationOption.SURFACE_SIZE),
                lambda: self.pick(plant),
                plant,
            ) for plant, offset in zip(plants, self.OFFSETS)
        ]

        self.manager.add_elements(*self.options)

    def render(self, screen: pygame.Surface) -> None:
        for option in self.options:
            option.render(screen)



class UIManager:
    __slots__ = ('event_manager', 'ui_elements')

    def __init__(self, event_manager: EventManager) -> None:
        self.event_manager = event_manager

        self.ui_elements: list[Element] = []

    def render(self, screen: pygame.Surface) -> None:
        for element in self.ui_elements:
            element.render(screen)

    def add_elements(self, *elements: Element) -> None:
        self.ui_elements.extend(elements)

    def remove_elements(self, *elements: Element) -> None:
        for element in elements:
            element.remove()
            self.ui_elements.remove(element)

