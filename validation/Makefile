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

# Users may need to source the .venv/bin/activate script to make sure
# that io-gen is in their PATH
IOGEN			:= io-gen
# Users probably need to source the settings64.sh script in the Vivado
# installation directory to make sure this is in their PATH
VIVADO			:= vivado

RUN_DRC			:= $(MAKEFILE_DIR)/run_drc.tcl
DRC_TCLARGS		:= $(PART) $(BOARD) $(DRC_XDC) $(DRC_REPORTS_DIR)
DRC_VIVADO_ARGS		:= -mode batch -log $(DRC_REPORTS_DIR)/vivado.log -journal $(DRC_REPORTS_DIR)/vivado.jou -notrace
STAMP_DRC_READY		:= $(DRC_DIR)/.stamp_drc_ready

RUN_SYNTH		:= $(MAKEFILE_DIR)/run_synth.tcl
SYNTH_TCLARGS		:= $(PART) $(BOARD) $(SYNTH_DIR) $(SYNTH_REPORTS_DIR)
SYNTH_VIVADO_ARGS	:= -mode batch -log $(SYNTH_REPORTS_DIR)/vivado.log -journal $(SYNTH_REPORTS_DIR)/vivado.jou -notrace
STAMP_SYNTH_READY	:= $(SYNTH_DIR)/.stamp_synth_ready

.PHONY: synth drc clean

synth: $(STAMP_SYNTH_READY)
	mkdir -pv $(SYNTH_REPORTS_DIR)
	$(VIVADO) $(SYNTH_VIVADO_ARGS) -source $(RUN_SYNTH) -tclargs $(SYNTH_TCLARGS)

drc: $(STAMP_DRC_READY)
	mkdir -pv $(DRC_REPORTS_DIR)
	cd $(SYNTH_DIR); $(VIVADO) $(DRC_VIVADO_ARGS) -source $(RUN_DRC) -tclargs $(DRC_TCLARGS)

$(STAMP_DRC_READY):
	mkdir -pv $(DRC_DIR)
	$(IOGEN) --top $(BOARD) --xdc-only --output $(DRC_DIR) $(BOARD_YAML)
	touch $(STAMP_DRC_READY)

$(STAMP_SYNTH_READY): $(SYNTH_DIR)/$(BOARD).v
	ln -sfv $(BOARD_DIR)/$(BOARD)_user.v $(SYNTH_DIR)/$(BOARD)_user.v
	patch $(SYNTH_DIR)/$(BOARD).v < $(BOARD_DIR)/$(BOARD).patch
	touch $(STAMP_SYNTH_READY)

$(SYNTH_DIR)/$(BOARD).v:
	mkdir -pv $(SYNTH_DIR)
	$(IOGEN) --top $(BOARD) --lang verilog --output $(SYNTH_DIR) $(BOARD_YAML)

clean:
	rm -rf $(MAKEFILE_DIR)/.Xil
	rm -rf $(OUTPUT_DIR)

