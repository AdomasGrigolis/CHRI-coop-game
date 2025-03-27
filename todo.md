**Last update (new tasks):** 19/03

# Program requirements  
- [x] Objects movement
	- [x] Objects can fall down
	- [x] Objects can free float, including some force mechanism that will slow them down
- [ ] Game interaction
	- [ ] Forces affect bodies
	- [ ] Body can be squished and broken
	- [ ] Force of the body affects the player experienced force
- [ ] Coop/multiplayer
	- [x] Two players can play
		- [x] Players can play on the same PC (might be difficult with multiple devices)
		- [ ] Players can play on different PCs (**to test**)
	- [x] Players can enter the program asynchronously
	- [x] Arbitration mechanism or lobby to choose which player is which (for example, who is left or right, who is color X or Y etc.)
	- [x] Force mechanism works with both (note that the simulation simply has been offloaded to the server)
- [ ] Visuals
	- [x] Can render all physics objects using pygame and not pymunk debug
	- [ ] Force indication
	- [ ] UI
		- [ ] In-game menu
		- [x] Lobby menu (not needed)
		- [ ] In-game UI
		- [ ] Debug and other
		- [ ] Settings (if there is time)
- [ ] Parameter adjustment so that it works well with haptic devices
- [ ] Data collection and analysis
	- [ ] Generate graphs
	- [ ] Record and get needed data for reporting or analysis

# Experiments  
- [ ] Find experiment subject (the thing that we are testing)
- [ ] Figure out a metric
- [ ] What conditions
	- [ ] Could be haptic device parameters etc.
- [ ] Running experiments
- [ ] etc. (please add)