import random



Color = tuple[int, int, int]



def get_similar_color(r: int, g: int, b: int) -> Color:
    return (
        random.randint(max(0, r - 5), min(255, r + 5)),
        random.randint(max(0, g - 5), min(255, g + 5)),
        random.randint(max(0, b - 5), min(255, b + 5)),
    )

