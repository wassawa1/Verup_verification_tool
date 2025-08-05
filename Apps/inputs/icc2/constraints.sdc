
# Clock definition
create_clock -period 10 -name clk [get_ports clk]

# Input/Output delays
set_input_delay -clock clk 2.0 [get_ports data_in*]
set_output_delay -clock clk 3.0 [get_ports data_out*]

# False paths
set_false_path -from [get_ports rst_n]
