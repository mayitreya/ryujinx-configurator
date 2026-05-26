# Ryujinx Configurator
When you want to quickly bind your controllers for Ryujinx directly from Steam Big Picture Mode

I recommend reading every point because this app can be really finnicky and 99% of problems can be solved by just reading this page :)

> [!NOTE]
> For those who believe that Linux terminal commands are daunting, I understand. I tried to make this as straightforward as possible to compile into an executable, but there are also releases under the releases tab if that's more your style, although that may not work depending on the Linux distro you're running. I really do recommend compiling this using Python tools as shown in the guide, it's really easy I promise.

## Overview
Personally, I've run into so many of these situations:

* You wanna play Mario Kart with the boys
* They bring their controllers
* You need to set up their controllers, and to do that, you need to switch to desktop mode, open Ryujinx, and bind everyone's controller
* It just takes way too much time, and your guests are waiting awkwardly (playing Brawl Stars while you slave away)
* "Wouldn't it be nice if I had a configuration app straight from big picture mode?" You think to yourself

And that's exactly what this application aims to tackle :)

Ryujinx Configurator provides a controller friendly, fullscreen interface that allows you to bind controller and keyboard buttons without needing to switch to a desktop environment or use a mouse (or even open Ryujinx's config window).

This tool is designed for couch gaming setups, allowing you to seamlessly configure multiple controllers for local multiplayer sessions without leaving the Big Picture interface.

## Compatibility
*This project works best with Steam Deck* (that's the only device I tested on apart from my PC running Nobara), but it should work with most Linux desktop setups. I have not tested Windows or macOS. That's for the community to help me with :)

## Installation & Build

This tool is a Python script that can be compiled into a standalone executable.

**Prerequisites:**
* Python 3.8 or higher (Steam Deck comes with 3.13 so you're good)
* Ryujinx installed and configured to an extent (like, you should at least add a controller and remove it just to create the Config.json file, y'know?)

**1. Clone the Repository**
```bash
git clone https://github.com/mayitreya/ryujinx-configurator.git
cd ryujinx-configurator
```

**2. Set up a Virtual Environment (It is recommended to use a virtual environment to avoid conflicts with system packages).**

My system packages conflicted with some of the packages for this app, so I really do recommend making a virtual environment to solve that

`cd` into the directory where `main.py` is. Then:

```bash
python3 -m venv build_env
source build_env/bin/activate
```

**3. Install Dependencies**
```bash
pip3 install -r requirements.txt
```

**4. Compile the script into a single executable file.**
```bash
pyinstaller --onefile --noconsole --name "Ryujinx Config Tool" main.py
```

The executable will be located in the `dist/` folder. You should copy the executable to the same directory as Ryujinx's Config.json file, wherever that may be for you. An easy way to check is to open Ryujinx (in desktop mode), then `File > Open Ryujinx Folder` and it should be there. Just paste your executable in that same place as Config.json.

# Setup in Steam
1. Open Steam in Desktop Mode.
2. Navigate to Games > Add a Non-Steam Game.
3. Browse and select the Ryujinx Config Tool executable from the Ryujinx folder (where you should have pasted the executable earlier :D).

**As of now, I seem to be running into a glitch with adding non-Steam games on Linux, it happens on both Steam Deck and my personal Linux PC. Keep reading to find out how to fix this!**

Return to Gaming Mode (or Big Picture Mode) so that you can launch the app. Also, it probably goes without mentioning, but you should connect your controllers to your device (Steam Deck, PC, whatever it is) by now, and make sure Steam controller input is properly configured. 

## Controls

| Action | Controller | Keyboard |
| --- | --- | --- |
| **Navigate** | D-Pad / Left Stick | Arrow Keys |
| **Select / Bind** | A / Cross | Enter |
| **Back / Cancel** | B / Circle | Esc |
| **Save & Exit** | Start | S |
| **Delete Config** | Nothing | R (while hovering over the player) |
| **Diagnostics** | Back / View / Select | D |

The **Diagnostics** overlay shows exactly what SDL (controller API) reports for each connected controller right now: its name, the GUID/id that will be written, its index, and whether input is being read through the normalized controller layer. Use it to sanity-check a controller before binding, and (see below) to confirm that this tool and Ryujinx see the same device.

## Important: launch this tool the same way you launch Ryujinx

This tool writes a config that points at a controller by its SDL GUID and name. The catch is that **some environments change what SDL sees.** Steam Input (when you launch through Big Picture Mode) hides your physical controller and presents a *virtual* one with a different GUID and a generic name. Game streaming like Moonlight does the same thing; your controllers show up as virtualized Xbox controllers on the host.

None of that is a problem **as long as you launch this tool and Ryujinx the same way**, because then both see the identical device:

| Configure tool via... | Launch Ryujinx via... | Works? |
| --- | --- | --- |
| Steam Big Picture | Steam Big Picture | Yes! |
| Independently (no Steam) | Independently (no Steam) | Yes! |
| Moonlight session | Moonlight session (same host) | Yes! |
| One way | A different way | No, because the bindings won't match :( |

If a controller you just configured shows up in Ryujinx as "Waiting for controller connection...", this mismatch is the most likely cause. Open the **Diagnostics** overlay (press `D`) in the tool and compare the `id`/`name` it shows against what Ryujinx lists in its own controller dropdown. They should be identical.

One more thing about **multiple identical controllers** (e.g. two of the same Xbox pad, or several pads streamed through Moonlight): they share a GUID and are told apart only by an index (`(0)`, `(1)`, ...). That index depends on the order the controllers connect, so an assignment made in one session may map to a different person's controller next session if they reconnect in a different order. That's a limitation of how the controllers identify themselves, not something this tool can work around.

# Art!
I created some really rudimentary art in Krita using Steam Grid DB images I found. Feel free to replace them with whatever you want. File name doesn't matter by the way, you do it through Steam.

## Issues?
This app can still be finnicky, and I appreciate any and all contributions from people much smarter than I am. Feel free to add an issue or a pull request :)

1. Can't add a non-Steam app because it just doesn't show up in the list even if you browse for it? Well, you should simply add an app that's already in the list of non-Steam apps and then just edit the properties to what you need. Just in case you need it, the config is here:

* Target: `"/home/may/.var/app/io.github.ryubing.Ryujinx/config/Ryujinx/Ryujinx Config Tool"` (obviously this one is mine, change it however you need to, also, quotes are required)
* Start in: `/home` (no quotes for this one)
* No launch options at all

2. Add any more common issues here and fixes to them, I haven't run into anything else

# Credits
Mayitreya Pasumarthy - Made with love :)
