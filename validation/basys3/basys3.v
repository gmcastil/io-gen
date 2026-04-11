module basys3 //#(
//)
(
    input   wire            clk_100m00_pad,
    input   wire [15:0]     slider_sw_pad,
    output  wire [15:0]     led_pad,
    output  wire [6:0]      seg_pad,
    output  wire [3:0]      digit_en_pad,
    output  wire            dp_pad,
    input   wire [4:0]      btn_pad,
    input   wire [3:0]      pmod_jxadc_p,
    input   wire [3:0]      pmod_jxadc_n,
    output  wire [3:0]      vga_red_pad,
    output  wire [3:0]      vga_blue_pad,
    output  wire [3:0]      vga_green_pad,
    output  wire            vga_hsync_pad,
    output  wire            vga_vsync_pad,
    // Schematic refers to this pin as TXD
    input   wire            uart_rx_pad,
    // Schematic refers to this pin as RXD
    output  wire            uart_tx_pad,
    inout   wire            ps2_clk_pad,
    inout   wire            ps2_data_pad,
    output  wire            spi_cs_n_pad,
    inout   wire            spi_sdi_pad,
    inout   wire            spi_sdo_pad,
    inout   wire            spi_wp_n_pad,
    inout   wire            spi_hld_n_pad
);

    wire            clk_100m00;
    wire [15:0]     slider_sw;
    wire [15:0]     led;
    wire [6:0]      seg;
    wire [3:0]      digit_en;
    wire            dp;
    wire [4:0]      btn;
    wire [3:0]      pmod_jxadc;
    wire [3:0]      vga_red;
    wire [3:0]      vga_blue;
    wire [3:0]      vga_green;
    wire            vga_hsync;
    wire            vga_vsync;
    wire            uart_rx;
    wire            uart_tx;
    wire            ps2_clk_i;
    wire            ps2_clk_o;
    wire            ps2_clk_t;
    wire            ps2_data_i;
    wire            ps2_data_o;
    wire            ps2_data_t;
    wire            spi_cs_n;
    wire            spi_sdi_i;
    wire            spi_sdi_o;
    wire            spi_sdi_t;
    wire            spi_sdo_i;
    wire            spi_sdo_o;
    wire            spi_sdo_t;
    wire            spi_wp_n_i;
    wire            spi_wp_n_o;
    wire            spi_wp_n_t;
    wire            spi_hld_n_i;
    wire            spi_hld_n_o;
    wire            spi_hld_n_t;

    basys3_io //#(
    //)
    basys3_io_i0 (
        .clk_100m00_pad (clk_100m00_pad),
        .clk_100m00     (clk_100m00),
        .slider_sw_pad  (slider_sw_pad),
        .slider_sw      (slider_sw),
        .led_pad        (led_pad),
        .led            (led),
        .seg_pad        (seg_pad),
        .seg            (seg),
        .digit_en_pad   (digit_en_pad),
        .digit_en       (digit_en),
        .dp_pad         (dp_pad),
        .dp             (dp),
        .btn_pad        (btn_pad),
        .btn            (btn),
        .pmod_jxadc_p   (pmod_jxadc_p),
        .pmod_jxadc_n   (pmod_jxadc_n),
        .pmod_jxadc     (pmod_jxadc),
        .vga_red_pad    (vga_red_pad),
        .vga_red        (vga_red),
        .vga_blue_pad   (vga_blue_pad),
        .vga_blue       (vga_blue),
        .vga_green_pad  (vga_green_pad),
        .vga_green      (vga_green),
        .vga_hsync_pad  (vga_hsync_pad),
        .vga_hsync      (vga_hsync),
        .vga_vsync_pad  (vga_vsync_pad),
        .vga_vsync      (vga_vsync),
        .uart_rx_pad    (uart_rx_pad),
        .uart_rx        (uart_rx),
        .uart_tx_pad    (uart_tx_pad),
        .uart_tx        (uart_tx),
        .ps2_clk_pad    (ps2_clk_pad),
        .ps2_clk_i      (ps2_clk_i),
        .ps2_clk_o      (ps2_clk_o),
        .ps2_clk_t      (ps2_clk_t),
        .ps2_data_pad   (ps2_data_pad),
        .ps2_data_i     (ps2_data_i),
        .ps2_data_o     (ps2_data_o),
        .ps2_data_t     (ps2_data_t),
        .spi_cs_n_pad   (spi_cs_n_pad),
        .spi_cs_n       (spi_cs_n),
        .spi_sdi_pad    (spi_sdi_pad),
        .spi_sdi_i      (spi_sdi_i),
        .spi_sdi_o      (spi_sdi_o),
        .spi_sdi_t      (spi_sdi_t),
        .spi_sdo_pad    (spi_sdo_pad),
        .spi_sdo_i      (spi_sdo_i),
        .spi_sdo_o      (spi_sdo_o),
        .spi_sdo_t      (spi_sdo_t),
        .spi_wp_n_pad   (spi_wp_n_pad),
        .spi_wp_n_i     (spi_wp_n_i),
        .spi_wp_n_o     (spi_wp_n_o),
        .spi_wp_n_t     (spi_wp_n_t),
        .spi_hld_n_pad  (spi_hld_n_pad),
        .spi_hld_n_i    (spi_hld_n_i),
        .spi_hld_n_o    (spi_hld_n_o),
        .spi_hld_n_t    (spi_hld_n_t)
    );

endmodule
