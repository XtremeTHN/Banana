[New banana re-writte](https://github.com/XtremeTHN/Vanana)

# Banana
A fnf gamebanana client. Tecnically is a gamebanana general client, you just need to change the `GAME_ID` variable from the `banana/modules/gamebanana/__init__.py` to your favorite game id from gamebanana.

## Features
- It has a download manager
- It can search submissions
- It can show the top submissions of the current game
- It can show the html from the submission description
- Currently, it can show the following submissions: Mod, Tool and Wip

## Dependencies
The package names are from arch repos.
- gtk4
- meson
- ninja
- python3
- libadwaita
- python-rich
- python-gobject
- python-requests
- blueprint-compiler
- python-beautifulsoup4

## Install
### General linux
Install all the dependencies, and then execute this:
```
meson setup build
meson install -C build
```

### NixOS
Add this repository to your flake inputs
```nix
# flake.nix
inputs.banana = {
  url = "github:XtremeTHN/Banana;
};
```
Then add Banana to the `home.packages` or `environment.systemPackages`.
```nix
# home.nix
home.packages = [
  inputs.banana.packages."x86_64-linux".default
];
```

## Preview
![preview](https://raw.githubusercontent.com/XtremeTHN/Banana/refs/heads/main/assets/preview1.png)
![search](https://raw.githubusercontent.com/XtremeTHN/Banana/refs/heads/main/assets/preview2.png)
![mod preview](https://raw.githubusercontent.com/XtremeTHN/Banana/refs/heads/main/assets/preview3.png)
