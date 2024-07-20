import pygame

from typing import Callable



ListernerID = tuple[int, int]
TimerID = int



class EventManager:
    __slots__ = ('key_pressed', 'button_pressed', 'listeners', 'timers', 'quit', 'mouse_pos', 'mouse_rel')

    def __init__(self) -> None:
        self.key_pressed: dict[int, bool] = {}
        self.button_pressed: dict[int, bool] = {}

        self.listeners: dict[int, dict[int, Callable[[pygame.Event], None]]] = {}
        self.timers: dict[int, tuple[float, Callable]] = {}

        self.quit = False

        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_rel = (0, 0)

    def update(self, dt: float) -> None:
        self.mouse_rel = (0, 0)

        for event in pygame.event.get():
            match event.type:
                # mouse buttons
                case pygame.MOUSEBUTTONDOWN:
                    self.button_pressed[event.button] = True
                case pygame.MOUSEBUTTONUP:
                    self.button_pressed[event.button] = False
                # keyboard
                case pygame.KEYDOWN:
                    self.key_pressed[event.key] = True
                case pygame.KEYUP:
                    self.key_pressed[event.key] = False
                # quit
                case pygame.QUIT:
                    self.quit = True
                # mouse position and motion
                case pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
                    self.mouse_rel = (self.mouse_rel[0] + event.rel[0], self.mouse_rel[1] + event.rel[1])

            if event.type in self.listeners:
                for listener in list(self.listeners[event.type].values()):
                    listener(event)

        for timer_id, timer in list(self.timers.items()):
            time_left = timer[0] - dt

            if time_left > 0:
                self.timers[timer_id] = (time_left, timer[1])

            else:
                timer[1]()
                
                self.remove_timer(timer_id)

    def add_listener(self, event_type: int, function: Callable[[pygame.Event], None]) -> ListernerID:
        if event_type not in self.listeners:
            self.listeners[event_type] = {}

        i = max(self.listeners[event_type], default=-1) + 1

        self.listeners[event_type][i] = function

        return event_type, i

    def remove_listeners(self, *listener_ids: ListernerID) -> None:
        for listener_event_type, listener_index in listener_ids:
            self.listeners[listener_event_type].pop(listener_index)

    def add_timer(self, time: float, function: Callable) -> TimerID:
        i = max(self.timers, default=-1) + 1

        self.timers[i] = (time, function)

        return i

    def remove_timer(self, timer_id: TimerID) -> None:
        self.timers.pop(timer_id)

    def is_key_pressed(self, key: int) -> bool:
        if key in self.key_pressed:
            return self.key_pressed[key]
        return False

    def is_button_pressed(self, key: int) -> bool:
        if key in self.button_pressed:
            return self.button_pressed[key]
        return False

