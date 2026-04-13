proc log_err { msg } {
    puts "Error: ${msg}"
}

proc usage { } {
    puts "Usage: vivado -mode batch -source run_drc.tcl -tclargs <part> <xdc_file> <rpt_file>"
    return 0
}

# Input argument checking
if { [llength $argv] != 3} {
    usage
    exit 1
}

# From tclargs - these should be validated prior to running 
set part [lindex $argv 0]
set xdc_file [lindex $argv 1]
set rpt_dir [lindex $argv 2]

set rpt_file [file rootname

set proj_name "drc-validation"

# Create an in-memory pin planning project
create_project -part "${part}" -in_memory -verbose "${proj_name}"
set_property DESIGN_MODE PinPlanning [current_fileset]

open_io_design -name "io_plan"
read_xdc "${xdc_file}"
report_drc -no_waivers -name drc_1 -ruledecks {default} -file "${rpt_file}"

close_project

