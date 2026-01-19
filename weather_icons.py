import sys
print("PYTHON EXEC:", sys.executable)

import json
import asyncio
import svgutils.transform as sg
import websockets
#import zmq
import os

async def main():
    print("directory: ",os.getcwd())

    async with websockets.serve(handler, "localhost", 5555):
        print("Starting Server")
        await asyncio.Future() #start server and then wait for JSON object result


async def handler(websocket):
    while True:
        #  Wait for next request from client
        message = await websocket.recv()
        print(f"Received request: {message}")
        message = json.loads(message)
        if not validate_weather(message):
            await websocket.send("Invalid Weather")
            continue
        weather = combine_weather(message)
        print(f"Combined Weather: {weather}")
        icon_svg = generate_icons(weather)
        print(f"Sending Icon: {icon_svg}")
        await websocket.send(icon_svg)


def validate_weather(weather):
    if not isinstance(weather, dict):
        return False
    if weather["sun"] > 3 or weather["sun"] < 0:
        return False
    if weather["rain"] > 4 or weather["rain"] < 0:
        return False
    if weather["snow"] > 3 or weather["snow"] < 0:
        return False
    if weather["clouds"] > 3 or weather["clouds"] < 0:
        return False
    if weather["wind"] > 3 or weather["wind"] < 0:
        return False
    if weather["rain"] > 1 and weather["clouds"] == 0:
        return False
    return True


def combine_weather(weather):
    new_weather = {
        "main_weather": None,
        "secondary_weather": None,
        "time": "day"
    }
    if not weather["sun"]:
        # If no sun, show a moon
        new_weather["time"] = "night"

    # Main Weather
    if weather["clouds"] > 0:
        # Cloud level 1 is a little cloudy, 2 is mostly cloudy, 3 is very cloudy
        new_weather["main_weather"] = f"cloudy{weather['clouds']}"
    elif weather["clouds"] == 0:
        # Clear weather
        new_weather["main_weather"] = "clear"

    # Secondary Weather
    if weather["rain"] == 4:
        # Lightning
        new_weather["secondary_weather"] = "lightning"
    elif weather["rain"] > 0 and weather["snow"] > 0:
        # If it is raining and snowing, show sleet
        new_weather["secondary_weather"] = "sleet"
    elif weather["rain"] > 0 and weather["wind"] > 0:
        # If it is raining and windy, show windy rain / Storm
        new_weather["secondary_weather"] = f"windy_rain{weather['rain']}"
    elif weather["rain"] > 0:
        # Rain
        new_weather["secondary_weather"] = f"rain{weather['rain']}"
    elif weather["snow"] > 0:
        # Snow
        new_weather["secondary_weather"] = f"snow{weather['snow']}"
        # Wind
    elif weather["wind"] > 0:
        new_weather["secondary_weather"] = f"wind{weather['wind']}"
    return new_weather


def generate_icons(new_weather):
    time, main_weather, secondary_weather = new_weather["time"], new_weather["main_weather"], new_weather["secondary_weather"]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "icons")
    
    fig = sg.SVGFigure(width="600px", height="600px")
    
    time_fig = sg.fromfile(os.path.join(icons_dir, f"{time}.svg")).getroot()

    fig.append([time_fig])
    
    if secondary_weather:
        secondary_fig = sg.fromfile(os.path.join(icons_dir, f"{secondary_weather}.svg")).getroot()
        secondary_fig.moveto(-10, 190)
        fig.append([secondary_fig])
    
    if main_weather != "clear":
        main_fig = sg.fromfile(os.path.join(icons_dir, f"{main_weather}.svg")).getroot()
        fig.append([main_fig])
        time_fig.moveto(190, -10)

    
    svg_bytes = fig.to_str()
    
    # Decode bytes to string
    svg_string = svg_bytes.decode('utf-8')
    
    # Add viewBox to crop the empty space
    svg_string = svg_string.replace(
        '<svg',
        '<svg viewBox="30 150 700 300"'
    )
    
    # Encode back to bytes for websocket
    return svg_string.encode('utf-8')


if __name__ == "__main__":
    asyncio.run(main()) #creates async event loop