# Broodcode Bot
This is the official bot for Broodcode, an system to automate your sandwich orders.

## Explanation
This bots checks every minute if it is 08:00 Friday. If it is and the link is still valid it will send a message containing the menu and the current payment link based in the `config.json`.
For checking the availability of the payment link, the bot creates a headless undetected chrome selenium browser and checks if there is an existing button that contains the text "Betaal", If yes it marks the link as valid, if no it will tag the breadmasters and mark the link as invalid.

Menu function was already a part of broodcode

## Commands:
- /check_link
  - Checks if the current link is still working or not
- /set_link
  - Set a different link as the payment link
- /menu
  - Displays the current menu

## TODO
- Link the broodcode_modules folder of broodcode and broodcode-bot
- Maybe create an logger that logs some info when a new payment came trough.
