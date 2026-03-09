// IO ring for example
// Port naming convention:
//   Pad-side ports use _pad (single-ended), _p/_n (differential)
//   Fabric-side ports use the signal name directly for in/out signals
//   Fabric-side tristate signals use _i (read from pad), _o (drive to pad),
//   _t (tristate enable, active high = output disabled)
//   Note: IOBUF primitive I/O are named from the primitive perspective:
//     IOBUF.I connects to gpio_o (fabric drives out)
//     IOBUF.O connects to gpio_i (fabric reads in)
module example_io (
    // 125 MHz system clock input
    input  wire        sys_clk_pad,
    output wire        sys_clk,

    // User LED outputs
    output wire [3:0]  led_pad,
    input  wire [3:0]  led,

    // 200 MHz differential reference clock input
    input  wire        ref_clk_p,
    input  wire        ref_clk_n,
    output wire        ref_clk,

    // LVDS serial data outputs
    output wire [2:0]  lvds_data_p,
    output wire [2:0]  lvds_data_n,
    input  wire [2:0]  lvds_data,

    // General purpose IO
    inout  wire [4:0]  gpio_pad,
    output wire [4:0]  gpio_i,
    input  wire [4:0]  gpio_o,
    input  wire [4:0]  gpio_t
);

    // 125 MHz system clock input
    IBUF ibuf_sys_clk (
        .I (sys_clk_pad),
        .O (sys_clk)
    );

    // User LED outputs
    OBUF obuf_led_0 (
        .I (led[0]),
        .O (led_pad[0])
    );
    OBUF obuf_led_1 (
        .I (led[1]),
        .O (led_pad[1])
    );
    OBUF obuf_led_2 (
        .I (led[2]),
        .O (led_pad[2])
    );
    OBUF obuf_led_3 (
        .I (led[3]),
        .O (led_pad[3])
    );

    // 200 MHz differential reference clock input
    IBUFDS ibufds_ref_clk (
        .I  (ref_clk_p),
        .IB (ref_clk_n),
        .O  (ref_clk)
    );

    // LVDS serial data outputs
    OBUFDS obufds_lvds_data_0 (
        .I  (lvds_data[0]),
        .O  (lvds_data_p[0]),
        .OB (lvds_data_n[0])
    );
    OBUFDS obufds_lvds_data_1 (
        .I  (lvds_data[1]),
        .O  (lvds_data_p[1]),
        .OB (lvds_data_n[1])
    );
    OBUFDS obufds_lvds_data_2 (
        .I  (lvds_data[2]),
        .O  (lvds_data_p[2]),
        .OB (lvds_data_n[2])
    );

    // General purpose IO
    IOBUF iobuf_gpio_0 (
        .IO (gpio_pad[0]),
        .I  (gpio_o[0]),
        .O  (gpio_i[0]),
        .T  (gpio_t[0])
    );
    IOBUF iobuf_gpio_1 (
        .IO (gpio_pad[1]),
        .I  (gpio_o[1]),
        .O  (gpio_i[1]),
        .T  (gpio_t[1])
    );
    IOBUF iobuf_gpio_2 (
        .IO (gpio_pad[2]),
        .I  (gpio_o[2]),
        .O  (gpio_i[2]),
        .T  (gpio_t[2])
    );
    IOBUF iobuf_gpio_3 (
        .IO (gpio_pad[3]),
        .I  (gpio_o[3]),
        .O  (gpio_i[3]),
        .T  (gpio_t[3])
    );
    IOBUF iobuf_gpio_4 (
        .IO (gpio_pad[4]),
        .I  (gpio_o[4]),
        .O  (gpio_i[4]),
        .T  (gpio_t[4])
    );

endmodule
