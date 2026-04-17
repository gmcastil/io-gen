proc log_err { msg } {
    puts "Error: ${msg}"
}

proc usage { } {
    puts "Usage: vivado -mode batch -source run_drc.tcl -tclargs <part> <board_name> <xdc_file> <reports_dir>"
    return 0
}

# Input argument checking
if { [llength $argv] != 4} {
    usage
    exit 1
}

# From tclargs - these should be validated prior to running 
set part [lindex $argv 0]
set board [lindex $argv 1]
set xdc_file [lindex $argv 2]
set reports_dir [lindex $argv 3]

set rpt_file "${reports_dir}/${board}.rpt"
set rpx_file "${reports_dir}/${board}.rpx"
set proj_name "drc-validation"

# Create an in-memory pin planning project
create_project -part "${part}" -in_memory -verbose "${proj_name}"
set_property DESIGN_MODE PinPlanning [current_fileset]

open_io_design -name "io_plan"
read_xdc "${xdc_file}"
report_drc -no_waivers -ruledecks {default} -file "${rpt_file}" -rpx "${rpx_file}"

close_project
exit

