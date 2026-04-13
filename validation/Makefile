SHELL		:= /bin/bash
MAKEFILE_DIR	:= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BOARD		:= basys3
BOARD_DIR	:= $(MAKEFILE_DIR)/$(BOARD)
BOARD_YAML	:= $(BOARD_DIR)/$(BOARD).yaml
OUTPUT_DIR	:= $(BOARD_DIR)/output
REPORTS_DIR	:= $(OUTPUT_DIR)/reports
BOARD_XDC	:= $(OUTPUT_DIR)/$(BOARD).xdc

include $(BOARD_DIR)/board.mk

MKDIR		:= mkdir
RM		:= rm
# Users may need to source the .venv/bin/activate script to make sure
# that io-gen is in their PATH
IOGEN		:= io-gen
# Users probably need to source the settings64.sh script in the Vivado
# installation directory to make sure this is in their PATH
VIVADO		:= vivado
# Put Vivado in batch mode and stick the journal and log in the output directory
VIVADO_ARGS	:= -mode tcl -log $(REPORTS_DIR)/vivado.log -journal $(REPORTS_DIR)/vivado.jou -notrace
VIVADO_TCLARGS	:= $(PART) $(BOARD) $(BOARD_XDC) $(REPORTS_DIR)
RUN_DRC		:= $(MAKEFILE_DIR)/run_drc.tcl

.PHONY: validate drc $(BOARD) clean

validate: drc

drc: $(BOARD)
	@$(MKDIR) -p $(REPORTS_DIR)
	@$(VIVADO) $(VIVADO_ARGS) -source $(RUN_DRC) -tclargs $(VIVADO_TCLARGS)

$(BOARD): $(BOARD_YAML)
	@$(MKDIR) -p $(OUTPUT_DIR)
	@$(IOGEN) --top $(BOARD) --lang verilog --output $(OUTPUT_DIR) $(BOARD_YAML)
	@$(IOGEN) --top $(BOARD) --lang vhdl --output $(OUTPUT_DIR) $(BOARD_YAML)

clean:
	@$(RM) -rf $(OUTPUT_DIR)
	@$(RM) -rf $(MAKEFILE_DIR)/.Xil

