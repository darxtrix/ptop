import npyscreen


SUPPORTED_THEMES = {
    'elegant'      : npyscreen.Themes.ElegantTheme,
    'colorful'     : npyscreen.Themes.ColorfulTheme,
    'simple'       : npyscreen.Themes.DefaultTheme,
    'dark'         : npyscreen.Themes.TransparentThemeDarkText,
    'light'        : npyscreen.Themes.TransparentThemeLightText,
    'blackonwhite' : npyscreen.Themes.BlackOnWhiteTheme
}

PRIVELAGED_USERS = [
    'root',
    'administrator'
]

INVALID_PROCESSES = [
	'zombie'
]

# This will be overriden by process sensor
SYSTEM_USERS = []