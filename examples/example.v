module example (
    // 125 MHz system clock input
    input  wire        sys_clk_pad,
    // User LED outputs
    output wire [3:0]  led_pad,
    // 200 MHz differential reference clock input
    input  wire        ref_clk_p,
    input  wire        ref_clk_n,
    // LVDS serial data outputs
    output wire [2:0]  lvds_data_p,
    output wire [2:0]  lvds_data_n,
    // General purpose IO
    inout  wire [4:0]  gpio_pad,
    // Spare output, driven directly
    output wire        spare_pad
);

    wire            sys_clk;
    wire    [3:0]   led;
    wire            ref_clk;
    wire    [2:0]   lvds_data;
    wire    [4:0]   gpio_i;
    wire    [4:0]   gpio_o;
    wire    [4:0]   gpio_t;

    example_io example_io_i0 (
        .sys_clk_pad   (sys_clk_pad),
        .sys_clk       (sys_clk),

        .led_pad       (led_pad),
        .led           (led),

        .ref_clk_p     (ref_clk_p),
        .ref_clk_n     (ref_clk_n),
        .ref_clk       (ref_clk),

        .lvds_data_p   (lvds_data_p),
        .lvds_data_n   (lvds_data_n),
        .lvds_data     (lvds_data),

        .gpio_pad      (gpio_pad),
        .gpio_i        (gpio_i),
        .gpio_o        (gpio_o),
        .gpio_t        (gpio_t)
    );

endmodule
