import pygame
import ui

from event import EventManager
from ui import UIManager
from plant import Plant, DrawSettings


pygame.init()



# main loop
window = pygame.display.set_mode((1335, 1000))
clock = pygame.Clock()

event_manager = EventManager()
ui_manager = UIManager(event_manager)

plant_window = ui.MutationWindow(ui_manager, Plant(Plant.ASPEN_GROWTH_RULES, Plant.ASPEN_AXIOM, Plant.ASPEN_DRAW_SETTINGS))

title_text = ui.Text(
    ui_manager,
    'Plant Generator',
    75,
    True,
    (0, 0, 0),
    (470, 95)
)

tree_preset_buttons = [
    ui.Button(
        ui_manager,
        pygame.Rect(905, 70, 105, 40),
        lambda: plant_window.pick(option=Plant(Plant.ASPEN_GROWTH_RULES, Plant.ASPEN_AXIOM, Plant.ASPEN_DRAW_SETTINGS)),
    ),
    ui.Button(
        ui_manager,
        pygame.Rect(905, 130, 105, 40),
        lambda: plant_window.pick(option=Plant(Plant.FERN_GROWTH_RULES, Plant.FERN_AXIOM, Plant.FERN_DRAW_SETTINGS)),
    ),
    ui.Button(
        ui_manager,
        pygame.Rect(1035, 70, 105, 40),
        lambda: plant_window.pick(option=Plant(Plant.LORAX_GROWTH_RULES, Plant.LORAX_AXIOM, Plant.LORAX_DRAW_SETTINGS)),
    ),
    ui.Button(
        ui_manager,
        pygame.Rect(1035, 130, 105, 40),
        lambda: plant_window.pick(option=Plant(Plant.BUSH_GROWTH_RULES, Plant.BUSH_AXIOM, Plant.BUSH_DRAW_SETTINGS)),
    ),
    ui.Button(
        ui_manager,
        pygame.Rect(1165, 70, 105, 40),
        lambda: plant_window.pick(option=Plant(Plant.SPOOKY_GROWTH_RULES, Plant.SPOOKY_AXIOM, Plant.SPOOKY_DRAW_SETTINGS)),
    ),
    ui.Button(
        ui_manager,
        pygame.Rect(1165, 130, 105, 40),
        lambda: plant_window.pick(option=Plant(Plant.get_random_rules(), 'X', DrawSettings.get_random())),
    ),
]

tree_preset_text = [
    ui.Text(
        ui_manager,
        'Plant Presets',
        20,
        True,
        (0, 0, 0),
        (tree_preset_buttons[2].bounding_box.centerx, 35),
    ),
    ui.Text(
        ui_manager,
        'Aspen',
        15,
        True,
        (0, 0, 0),
        tree_preset_buttons[0].bounding_box.center,
    ),
    ui.Text(
        ui_manager,
        'Fern',
        15,
        True,
        (0, 0, 0),
        tree_preset_buttons[1].bounding_box.center,
    ),
    ui.Text(
        ui_manager,
        'Lorax',
        15,
        True,
        (0, 0, 0),
        tree_preset_buttons[2].bounding_box.center,
    ),
    ui.Text(
        ui_manager,
        'Bush',
        15,
        True,
        (0, 0, 0),
        tree_preset_buttons[3].bounding_box.center,
    ),
    ui.Text(
        ui_manager,
        'Spooky',
        15,
        True,
        (0, 0, 0),
        tree_preset_buttons[4].bounding_box.center,
    ),
    ui.Text(
        ui_manager,
        'Randomize',
        15,
        True,
        (0, 0, 0),
        tree_preset_buttons[5].bounding_box.center,
    ),
]

ui_manager.add_elements(plant_window, title_text, *tree_preset_buttons, *tree_preset_text)

running = True



while running:
    dt = clock.tick(60) * 0.001

    event_manager.update(dt)

    if event_manager.quit or event_manager.is_key_pressed(pygame.K_ESCAPE):
        running = False

    window.fill((200, 200, 200))

    ui_manager.render(window)

    pygame.display.flip()


pygame.quit()

