from libqtile.config import Click, Drag, Group, Key, Match, Screen, ScratchPad, DropDown
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile import qtile, hook, layout, qtile, widget, bar
from libqtile.command import lazy
from subprocess import *
from typing import TYPE_CHECKING
from libqtile.backend import base
from libqtile.widget import *
import subprocess
from libqtile.widget.backlight import ChangeDirection
from libqtile.widget.battery import Battery, BatteryState
import asyncio
import importlib
import os
import sys

mod = "mod4"
terminal = "konsole"

keys = [
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "shift"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),

    Key([mod, "control"], "r", lazy.restart(), desc="Restart Qtile"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawncmd(),
        desc="Spawn a command using a prompt widget"),
    Key([mod], "space", lazy.widget['keyboardlayout'].next_keyboard(), desc='Next keyboard layout.'),
]

group_names = [("WWW", {'layout': 'max', 'spawn':'firefox'}),
               ("DEV", {'layout': 'treetab'}),
               ("CHAT", {'layout': 'max'}),
               ("CMD", {'layout': 'columns', 'spawn':'konsole'}),
               ("TOR", {'layout': 'floating'}),
               ("PIC", {'layout': 'max'}),
               ("DOC", {'layout': 'columns'}),
               ]

groups = [Group(name, **kwargs) for name, kwargs in group_names]

for i, (name, kwargs) in enumerate(group_names, 1):
    keys.append(Key([mod], str(i), lazy.group[name].toscreen()))        # Switch to another group
    keys.append(Key([mod, "shift"], str(i), lazy.window.togroup(name))) # Send current window to another group

layouts = [
    layout.Columns(
        border_focus=None,
        border_normal='202020',
        border_width=2,
    ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
    layout.TreeTab(
         fontsize = 13,
         sections = ["   TABS OPEN\n"],
         section_fontsize = 15,
         font='sans',
         bg_color = "181818",
         active_bg = "505050",
         active_fg = "ffffff",
         inactive_bg = "303030",
         inactive_fg = "ffffff",
         padding_left = 0,
         padding_x = 0,
         padding_y = 7,
         section_top = 22,
         section_bottom = 30,
         level_shift = 8,
         vspace = 14,
         panel_width = 200,
         border_width = 0,

         #bg_color = "#181818",
         #active_bg = "7979d2",
         #active_fg = "ffffff",
         #inactive_bg = "52527a",
         #inactive_fg = "ffffff",
    ),
    layout.Floating(
        border_width=0
    ),
]

widget_defaults = dict(
    font='sans',
    fontsize=13,
)
extension_defaults = widget_defaults.copy()

def change_layout():
     qtile.cmd_next_layout()

def spawn_firefox():
    qtile.cmd_spawn('firefox')

def spawn_vscodium():
    qtile.cmd_spawn('vscodium')

def spawn_terminal():
    qtile.cmd_spawn(terminal)

def spawn_element():
    qtile.cmd_spawn('element-desktop')

def spawn_gimp():
    qtile.cmd_spawn('gimp')

def spawn_spacefm():
    qtile.cmd_spawn('spacefm')

def spawn_tor():
    qtile.cmd_spawn('tor-browser')
    qtile.cmd_spawn(terminal + ' -e nyx')

class MyVolume(widget.Volume):
    def _configure(self, qtile, bar):
        widget.Volume._configure(self, qtile, bar)
        self.volume = self.get_volume()
        self.text = ''
        if self.volume <= 0:
            self.text = ''
        elif self.volume <= 15:
            self.text = ''
        elif self.volume < 50:
            self.text = ''
        else:
            self.text = ''
        
    def _update_drawer(self, wob=True):
        if self.volume <= 0:
            self.text = ''
        elif self.volume <= 15:
            self.text = ''
        elif self.volume < 50:
            self.text = ''
        else:
            self.text = ''
        self.draw()

    def cmd_mute(self):
        subprocess.call('amixer set Master toggle'.split())
        self.channel = 'Master'
        self.volume = self.get_volume()
        self.channel = 'PCM'
        if self.volume == 0:
            self.volume = self.get_volume()
        self._update_drawer(wob=False)

volume = MyVolume(
    fontsize=18,
    font='Font Awesome 5 Free',
    foreground='ffffff',
    update_interval=None,
)

class MyBattery(Battery):
    def build_string(self, status):
        if self.layout is not None:
            if status.state == BatteryState.DISCHARGING and status.percent < self.low_percentage:
                self.layout.colour = self.low_foreground
            else:
                self.layout.colour = self.foreground
        if status.state == BatteryState.DISCHARGING:
            if status.percent > 0.75:
                char = ''
            elif status.percent > 0.45:
                char = ''
            else:
                char = ''
        elif status.percent >= 1 or status.state == BatteryState.FULL:
            char = ''
        elif status.state == BatteryState.EMPTY or \
                (status.state == BatteryState.UNKNOWN and status.percent == 0):
            char = ''
        else:
            char = ''
        return self.format.format(char=char, percent=status.percent)

    def restore(self):
        self.format = '{char}'
        self.font = 'Font Awesome 5 Free'
        self.timer_setup()

    def button_press(self, x, y, button):
        self.format = '{percent:2.0%}'
        self.font = 'TamzenForPowerline Bold'
        self.timer_setup()
        self.timeout_add(1, self.restore)


battery = MyBattery(
    format='{char}',
    low_foreground='7979d2',
    show_short_text=False,
    low_percentage=0.12,
    foreground='#ffffff',
    notify_below=12,
    fontsize=19
)


screens = [
    Screen(
        top=bar.Bar(
            [   
                widget.TextBox(
                    font = 'Font Awesome 5 Free',
                    fmt = '',
                    mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn("hefflogout")},
                    fontsize = 22,
                ),
                widget.Sep(
                    linewidth = 35,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.GroupBox(
                       fontsize = 12,
                       margin_y = 6,
                       margin_x = 0,
                       padding_y = 5,
                       padding_x = 3,
                       borderwidth = 3,
                       font='sans bold',
                       active_fg = 'ffffff',
                       inactive = '707070',
                       rounded = False,
                       highlight_color = '#3d3f4b',
                       highlight_method = "line",
                       this_current_screen_border = '7979d2',
                       background = '202020',
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                
                widget.CurrentLayoutIcon(
                    padding = 0,
                    scale = 0.7
                ),
                widget.CurrentLayout(
                    font='sans bold',
                ),
                widget.Prompt(
                    prompt='Spawn: ',
                    foreground = 'ffffff',
                    fontsize=13,
                ),
                widget.TextBox(
                    fmt = '',
                    font = 'Font Awesome 5 Free',
                    padding=30,
                    fontsize = 17,
                    mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(str("scrot -e 'mv $f ~/ScreenShots'"))}
                ),
                
                widget.WindowName(
                    fontsize=13,
                    font='sans bold',
                    max_chars = 1,
                    format='',
                    linewidth=0
                ),

                widget.Chord(
                    chords_colors={
                        'launch': ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/firefoxtest1.png',
                    margin = 8,
                    mouse_callbacks = {'Button1': spawn_firefox},
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                
                widget.Image(
                    filename = '~/.config/qtile/Pictures/torbwosernew.png',
                    margin = 7,
                    mouse_callbacks = {'Button1': spawn_tor},
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/vscodium2.png',
                    margin = 1,
                    mouse_callbacks = {'Button1': spawn_vscodium},
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/terminal1.png',
                    margin = 7,
                    mouse_callbacks = {'Button1': spawn_terminal},
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/elementdesktop1.png',
                    margin = 8,
                    mouse_callbacks = {'Button1': spawn_element},
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/gimp1.png',
                    margin = 7,
                    mouse_callbacks = {'Button1': spawn_gimp},
                ),
                widget.Sep(
                    linewidth = 40,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/folder.png',
                    margin = 7,
                    mouse_callbacks = {'Button1': spawn_spacefm},
                ),
                widget.Sep(
                    linewidth = 160,
                    foreground = '202020',
                    background = '202020'
                ),
                battery,
                widget.Sep(
                    linewidth = 30,
                    foreground = '202020',
                    background = '202020'
                ),
                volume,
                widget.Volume(
                    fontsize=18,
                    font='sans bold',
                    foreground='ffffff',
                    mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn("pavucontrol")},
                    padding=5
                ),
                widget.Sep(
                    linewidth = 26,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/download1.png',
                    margin = 10,
                    mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(terminal + ' -e sudo pacman -Syu')}, 
                ),
                widget.CheckUpdates(
                    no_update_string='0',
                    display_format="{updates} Updates",
                    update_interval=1800,
                    custom_command='checkupdates',
                    font='sans bold',
                    mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(terminal + ' -e sudo pacman -Syu')},
                ),
                widget.KeyboardLayout(
                    padding = 38,
                    configured_keyboards = ['us', 'cz'],
                    font='sans bold',
                ),
                widget.Image(
                    filename = '~/.config/qtile/Pictures/callendar1.png',
                    margin = 11,
                ),
                widget.Clock(format='%d/%m/%g', font='sans bold'),
                widget.Sep(
                    linewidth = 18,
                    foreground = '202020',
                    background = '202020'
                ),
                widget.Clock(
                    fontsize=20,
                    font='sans bold',
                    update_interval=60,
                )
            ],
            size = 40,
            background = '#202020',
        ),

    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(border_width = 2, border_normal='202020', border_focus='202020', float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
])
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True

wmname = "LG3D"