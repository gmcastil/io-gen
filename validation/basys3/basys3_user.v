module basys3_user //#(
//)
(
    input   wire            clk_100m00,
    input   wire [15:0]     slider_sw,
    output  wire [15:0]     led,
    output  wire [6:0]      seg,
    output  wire [3:0]      digit_en,
    output  wire            dp,
    input   wire [4:0]      btn,
    input   wire [3:0]      pmod_jxadc,
    output  wire [3:0]      vga_red,
    output  wire [3:0]      vga_blue,
    output  wire [3:0]      vga_green,
    output  wire            vga_hsync,
    output  wire            vga_vsync,
    input   wire            uart_rx,
    output  wire            uart_tx,
    input   wire            ps2_clk_i,
    output  wire            ps2_clk_o,
    output  wire            ps2_clk_t,
    input   wire            ps2_data_i,
    output  wire            ps2_data_o,
    output  wire            ps2_data_t,
    output  wire            spi_cs_n,
    input   wire            spi_sdi_i,
    output  wire            spi_sdi_o,
    output  wire            spi_sdi_t,
    input   wire            spi_sdo_i,
    output  wire            spi_sdo_o,
    output  wire            spi_sdo_t,
    input   wire            spi_wp_n_i,
    output  wire            spi_wp_n_o,
    output  wire            spi_wp_n_t,
    input   wire            spi_hld_n_i,
    output  wire            spi_hld_n_o,
    output  wire            spi_hld_n_t
);

    reg jxadc_bit;

    // Use slider switches as inputs to drive the O and T pins of the IO
    // primitive and the LEDs as sinks for the I pin.
    assign led[0]       = ps2_clk_i;
    assign ps2_clk_o    = slider_sw[0];
    assign ps2_clk_t    = btn[0];

    assign ps2_data_o   = slider_sw[1];
    assign led[1]       = ps2_data_i;
    assign ps2_data_t   = btn[1];

    assign spi_sdi_o    = slider_sw[2];
    assign led[2]       = spi_sdi_i;
    assign spi_sdi_t    = btn[2];

    assign spi_sdo_o    = slider_sw[3];
    assign led[3]       = spi_sdo_i;
    assign spi_sdo_t    = btn[3];

    assign spi_wp_n_o   = slider_sw[4];
    assign led[4]       = spi_wp_n_i;
    assign spi_wp_n_t   = btn[4];

    assign spi_hld_n_o  = slider_sw[5];
    assign led[5]       = spi_hld_n_i;
    assign spi_hld_n_t  = slider_sw[6];

    // Drive the chip select with a constant
    assign spi_cs_n     = 1'b1;

    // All the VGA stuff can be tied off, the tool still needs to drive it
    assign vga_red      = 4'h0; 
    assign vga_blue     = 4'h0;
    assign vga_green    = 4'h0;
    assign vga_hsync    = 1'b0;
    assign vga_vsync    = 1'b0;

    // Sink UART RX to an LED so it doesn't get pruned, and drive the TX with 0
    assign led[6]       = uart_rx;
    assign uart_tx      = 1'b0;

    // All the 7-segment stuff can be zeroed out
    assign seg          = 7'h0;
    assign digit_en     = 4'h0;
    assign dp           = jxadc_bit;

    // That leaves sliders 15:7 and LED 15:7, so just pair those up
    assign led[15:7]    = slider_sw[15:7];
            
    // Reduce all the PMOD XADC bits to one bit and drive the decimal point
    always @(posedge clk_100m00) begin
        jxadc_bit   <= | pmod_jxadc;
    end

endmodule
