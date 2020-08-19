# ChooseDice

A utility for cheating in Super Mario Party (or similar dice based games), that displays the optimal dice and direction choice to maximize the expected number of times landed on one or more goal locations in a given number of turns.

![Demo Image](https://user-images.githubusercontent.com/22622734/90078996-7e0d0900-dcbb-11ea-8018-ebbae04edf20.png)

## Usage

On a python environment including the TkInter package, run:

```
python choosedice.py
```

Once in the GUI:
* Left click to place a board space

* Right click on a board space and...
  * release on another space to connect/disconnect them
  * release on the same space to delete that space

* Left click 'Set next node clicked to origin' and then left click on a space to set the starting position

* Left click 'Toggle next clicked node goal state' and then left click on a space to toggle its status as a goal space

* Left click 'Add character' to add another character dice

* Left click 'Remove character' to remove the last added character dice

* Select the character dice from each of the drop-down menus

* Select the number of turns to solve for by dragging the '# of turns' slider

* Left click 'Solve' to show the expected number of goal spaces achieved and the optimal choices for each roll
