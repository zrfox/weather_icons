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
    time, main_weather, secondary_weather = new_weather["time"], new_weather["main_weather"], new_weather[
        "secondary_weather"]
    fig = sg.SVGFigure("1cm", "1cm") #changed from "5in" #idk if this is doing much
    
    time_fig = sg.fromfile(f"./icons/{time}.svg").getroot()
    if main_weather != "clear":
        time_fig.moveto(120, -50)  # Move over to the top right, so it can peek out from behind main
    fig.append([time_fig])
    # May sometimes be None
    if secondary_weather:
        secondary_fig = sg.fromfile(f"./icons/{secondary_weather}.svg").getroot()
        if secondary_weather != 0:
            secondary_fig.moveto(0, 200)  # Needs to be overlapping slightly with main
        fig.append([secondary_fig])
    # Clear doesn't need an icon
    if main_weather != "clear":
        main_fig = sg.fromfile(f"./icons/{main_weather}.svg").getroot() #was "./weather_icons/icons/{main_weather}.svg"
        fig.append([main_fig])
    return fig.to_str()


if __name__ == "__main__":
    asyncio.run(main()) #creates async event loop