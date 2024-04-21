deploy:
	rsync -av --delete config_key.py main.py feathers2.py homie.py lib /Volumes/CIRCUITPY/
