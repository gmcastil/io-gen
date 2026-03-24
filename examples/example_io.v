module example_io (
    input  wire        sys_clk_pad,
    output wire        sys_clk,

    output wire [3:0]  led_pad,
    input  wire [3:0]  led,

    input  wire        ref_clk_p,
    input  wire        ref_clk_n,
    output wire        ref_clk,

    output wire [2:0]  lvds_data_p,
    output wire [2:0]  lvds_data_n,
    input  wire [2:0]  lvds_data,

    inout  wire [4:0]  gpio_pad,
    output wire [4:0]  gpio_i,
    input  wire [4:0]  gpio_o,
    input  wire [4:0]  gpio_t
);

    IBUF ibuf_sys_clk_i0 (
        .I (sys_clk_pad),
        .O (sys_clk)
    );

    OBUF obuf_led_i0 (
        .I (led[0]),
        .O (led_pad[0])
    );
    OBUF obuf_led_i1 (
        .I (led[1]),
        .O (led_pad[1])
    );
    OBUF obuf_led_i2 (
        .I (led[2]),
        .O (led_pad[2])
    );
    OBUF obuf_led_i3 (
        .I (led[3]),
        .O (led_pad[3])
    );

    IBUFDS ibufds_ref_clk_i0 (
        .I  (ref_clk_p),
        .IB (ref_clk_n),
        .O  (ref_clk)
    );

    OBUFDS obufds_lvds_data_i0 (
        .I  (lvds_data[0]),
        .O  (lvds_data_p[0]),
        .OB (lvds_data_n[0])
    );
    OBUFDS obufds_lvds_data_i1 (
        .I  (lvds_data[1]),
        .O  (lvds_data_p[1]),
        .OB (lvds_data_n[1])
    );
    OBUFDS obufds_lvds_data_i2 (
        .I  (lvds_data[2]),
        .O  (lvds_data_p[2]),
        .OB (lvds_data_n[2])
    );

    IOBUF iobuf_gpio_i0 (
        .IO (gpio_pad[0]),
        .I  (gpio_o[0]),
        .O  (gpio_i[0]),
        .T  (gpio_t[0])
    );
    IOBUF iobuf_gpio_i1 (
        .IO (gpio_pad[1]),
        .I  (gpio_o[1]),
        .O  (gpio_i[1]),
        .T  (gpio_t[1])
    );
    IOBUF iobuf_gpio_i2 (
        .IO (gpio_pad[2]),
        .I  (gpio_o[2]),
        .O  (gpio_i[2]),
        .T  (gpio_t[2])
    );
    IOBUF iobuf_gpio_i3 (
        .IO (gpio_pad[3]),
        .I  (gpio_o[3]),
        .O  (gpio_i[3]),
        .T  (gpio_t[3])
    );
    IOBUF iobuf_gpio_i4 (
        .IO (gpio_pad[4]),
        .I  (gpio_o[4]),
        .O  (gpio_i[4]),
        .T  (gpio_t[4])
    );

endmodule
