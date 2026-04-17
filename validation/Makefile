SHELL			:= /bin/bash
MAKEFILE_DIR		:= $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

BOARD			:= basys3
BOARD_DIR		:= $(MAKEFILE_DIR)/$(BOARD)
BOARD_YAML		:= $(BOARD_DIR)/$(BOARD).yaml
OUTPUT_DIR		:= $(BOARD_DIR)/output

DRC_DIR			:= $(OUTPUT_DIR)/drc
DRC_REPORTS_DIR		:= $(DRC_DIR)/reports
DRC_XDC			:= $(DRC_DIR)/$(BOARD).xdc

SYNTH_DIR		:= $(OUTPUT_DIR)/synth
SYNTH_REPORTS_DIR	:= $(SYNTH_DIR)/reports

include $(BOARD_DIR)/board.mk


MKDIR			:= mkdir
RM			:= rm
LN			:= ln
TOUCH			:= touch
PATCH			:= patch
# Users may need to source the .venv/bin/activate script to make sure
# that io-gen is in their PATH
IOGEN			:= io-gen
# Users probably need to source the settings64.sh script in the Vivado
# installation directory to make sure this is in their PATH
VIVADO			:= vivado
# Put Vivado in batch mode and stick the journal and log in the output directory
DRC_VIVADO_ARGS		:= -mode batch -log $(DRC_REPORTS_DIR)/vivado.log -journal $(DRC_REPORTS_DIR)/vivado.jou -notrace
SYNTH_VIVADO_ARGS	:= -mode batch -log $(SYNTH_REPORTS_DIR)/vivado.log -journal $(SYNTH_REPORTS_DIR)/vivado.jou -notrace

RUN_DRC			:= $(MAKEFILE_DIR)/run_drc.tcl
DRC_TCLARGS		:= $(PART) $(BOARD) $(DRC_XDC) $(DRC_REPORTS_DIR)

RUN_SYNTH		:= $(MAKEFILE_DIR)/run_synth.tcl
SYNTH_TCLARGS		:= $(PART) $(BOARD) $(SYNTH_DIR) $(SYNTH_REPORTS_DIR)

STAMP_DRC_READY		:= $(DRC_DIR)/.stamp_drc_ready
STAMP_SYNTH_READY	:= $(SYNTH_DIR)/.stamp_synth_ready

.PHONY: synth drc $(BOARD) clean

synth: $(STAMP_SYNTH_READY)
	@$(MKDIR) -pv $(SYNTH_REPORTS_DIR)
	@$(VIVADO) $(SYNTH_VIVADO_ARGS) -source $(RUN_SYNTH) -tclargs $(SYNTH_TCLARGS)

drc: $(STAMP_DRC_READY)
	@$(MKDIR) -pv $(DRC_REPORTS_DIR)
	@$(VIVADO) $(DRC_VIVADO_ARGS) -source $(RUN_DRC) -tclargs $(DRC_TCLARGS)

$(STAMP_DRC_READY):
	@$(MKDIR) -pv $(DRC_DIR)
	@$(IOGEN) --top $(BOARD) --xdc-only --output $(DRC_DIR) $(BOARD_YAML)
	@$(TOUCH) $(STAMP_DRC_READY)

$(STAMP_SYNTH_READY): $(SYNTH_DIR)/$(BOARD).v
	@$(LN) -sfv $(BOARD_DIR)/$(BOARD)_user.v $(SYNTH_DIR)/$(BOARD).patch
	@$(PATCH) $(SYNTH_DIR)/$(BOARD)_user.v < $(BOARD_DIR)/$(BOARD).patch
	@$(TOUCH) $(STAMP_SYNTH_READY)

$(SYNTH_DIR)/$(BOARD).v:
	@$(MKDIR) -pv $(SYNTH_DIR)
	@$(IOGEN) --top $(BOARD) --lang verilog --output $(SYNTH_DIR) $(BOARD_YAML)

clean:
	$(RM) -rf $(MAKEFILE_DIR)/.Xil
	$(RM) -rf $(OUTPUT_DIR)

