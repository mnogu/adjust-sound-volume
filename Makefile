INPUTS = __init__.py config.json manifest.json
OUTPUT = adjust-sound-volume.ankiaddon

$(OUTPUT): $(INPUTS)
	zip $(OUTPUT) $(INPUTS)
