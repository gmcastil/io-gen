SHELL		:= /bin/bash

MKDIR		:= mkdir

IOGEN		:= io-gen

BOARD		:= basys3
OUTPUT_DIR	:= $(PWD)/$(BOARD)

.PHONY: $(BOARD)
$(BOARD): $(BOARD).yaml
	$(MKDIR) -pv $(OUTPUT_DIR)
	$(IOGEN) --top $(BOARD) --lang verilog --output $(OUTPUT_DIR) $(BOARD).yaml
	$(IOGEN) --top $(BOARD) --lang vhdl --output $(OUTPUT_DIR) $(BOARD).yaml

clean:
	$(RM) -rf basys3

