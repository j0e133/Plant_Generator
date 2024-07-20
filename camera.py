


vec2 = tuple[float, float]



class Camera:
    __slots__ = ('_offset', '_zoom', '_inv_zoom')

    def __init__(self, offset: vec2 = (0, 0), zoom: float = 1) -> None:
        self._offset = offset
        self._zoom = zoom
        self._inv_zoom = 1 / zoom

    def transform(self, point: vec2) -> vec2:
        return ((point[0] + self._offset[0]) * self._zoom, (point[1] + self._offset[1]) * self._zoom)
    
    def scale(self, value: float) -> float:
        return value * self._inv_zoom
    
    def move(self, movement: vec2) -> None:
        self._offset = (self._offset[0] + movement[0], self._offset[1] + movement[1])
    
    def scaled_move(self, movement: vec2) -> None:
        self._offset = (self._offset[0] + movement[0] * self._inv_zoom, self._offset[1] + movement[1] * self._inv_zoom)

    def zoom(self, multiplier: float) -> None:
        self._zoom *= multiplier
        self._inv_zoom = 1 / self._zoom
    

