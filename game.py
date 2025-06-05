from js import document

canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")

# Example: Draw background
def draw_background():
    ctx.fillStyle = "black"
    ctx.fillRect(0, 0, canvas.width, canvas.height)

# Example: Draw a player square
def draw_player(x, y):
    ctx.fillStyle = "lime"
    ctx.fillRect(x, y, 40, 40)

# Simple game loop using setInterval
from pyodide.ffi import create_proxy
import asyncio

x = 380
y = 550

def game_loop():
    global x, y
    draw_background()
    draw_player(x, y)
    # You could update x/y here to animate or respond to input

game_loop_proxy = create_proxy(game_loop)
js.setInterval(game_loop_proxy, 33)  # ~30 FPS
