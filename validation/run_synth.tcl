proc log_err { msg } {
    puts "Error: ${msg}"
}

proc usage { } {
    puts "Usage: vivado -mode batch -source run_synth.tcl -tclargs <part> <board_name> <src_dir> <reports_dir>"
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
set src_dir [lindex $argv 2]
set reports_dir [lindex $argv 3]

read_verilog "${src_dir}/${board}.v"
read_verilog "${src_dir}/${board}_io.v"
read_verilog "${src_dir}/${board}_user.v"
read_xdc "${src_dir}/${board}.xdc"

synth_design -top ${board} -part ${part}
opt_design
place_design
route_design

report_utilization -file "${reports_dir}/${board}_utilization.rpt"
write_bitstream -force "${reports_dir}/../${board}.bit"

exit
