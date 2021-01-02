INPUTS = __init__.py config.json manifest.json
OUTPUT = adjust-sound-volume.ankiaddon

$(OUTPUT): $(INPUTS)
	if [ -f $(OUTPUT) ]; then rm $(OUTPUT); fi
	zip $(OUTPUT) $(INPUTS)
