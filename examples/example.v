module example //#(
//)
(
    // 125 MHz system clock input
    input   wire            sys_clk_pad,
    // User LED outputs
    output  wire [3:0]      led_pad,
    // User LED output, buffer inferred
    output  wire            user_led_pad,
    // 200 MHz differential reference clock input
    input   wire            ref_clk_p,
    input   wire            ref_clk_n,
    // LVDS serial data outputs
    output  wire [2:0]      lvds_data_p,
    output  wire [2:0]      lvds_data_n,
    // General purpose IO
    inout   wire [4:0]      gpio_pad,
    // Spare output, driven directly
    output  wire            spare_pad,
    // Differential general IO
    inout   wire            diff_io_p,
    inout   wire            diff_io_n
);

    wire            sys_clk;
    wire [3:0]      led;
    wire            user_led;
    wire            ref_clk;
    wire [2:0]      lvds_data;
    wire [4:0]      gpio_i;
    wire [4:0]      gpio_o;
    wire [4:0]      gpio_t;
    wire            diff_io_i;
    wire            diff_io_o;
    wire            diff_io_t;

    example_io //#(
    //)
    example_io_i0 (
        .sys_clk_pad    (sys_clk_pad),
        .sys_clk        (sys_clk),
        .led_pad        (led_pad),
        .led            (led),
        .user_led_pad   (user_led_pad),
        .user_led       (user_led),
        .ref_clk_p      (ref_clk_p),
        .ref_clk_n      (ref_clk_n),
        .ref_clk        (ref_clk),
        .lvds_data_p    (lvds_data_p),
        .lvds_data_n    (lvds_data_n),
        .lvds_data      (lvds_data),
        .gpio_pad       (gpio_pad),
        .gpio_i         (gpio_i),
        .gpio_o         (gpio_o),
        .gpio_t         (gpio_t),
        .diff_io_p      (diff_io_p),
        .diff_io_n      (diff_io_n),
        .diff_io_i      (diff_io_i),
        .diff_io_o      (diff_io_o),
        .diff_io_t      (diff_io_t)
    );

endmodule
