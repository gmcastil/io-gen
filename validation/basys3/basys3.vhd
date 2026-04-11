library ieee;
use ieee.std_logic_1164.all;

entity basys3 is
    -- generic (
    -- )
    port (
        clk_100m00_pad  : in    std_logic;
        slider_sw_pad   : in    std_logic_vector(15 downto 0);
        led_pad         : out   std_logic_vector(15 downto 0);
        seg_pad         : out   std_logic_vector(6 downto 0);
        digit_en_pad    : out   std_logic_vector(3 downto 0);
        dp_pad          : out   std_logic;
        btn_pad         : in    std_logic_vector(4 downto 0);
        pmod_jxadc_p    : in    std_logic_vector(3 downto 0);
        pmod_jxadc_n    : in    std_logic_vector(3 downto 0);
        vga_red_pad     : out   std_logic_vector(3 downto 0);
        vga_blue_pad    : out   std_logic_vector(3 downto 0);
        vga_green_pad   : out   std_logic_vector(3 downto 0);
        vga_hsync_pad   : out   std_logic;
        vga_vsync_pad   : out   std_logic;
        -- Schematic refers to this pin as TXD
        uart_rx_pad     : in    std_logic;
        -- Schematic refers to this pin as RXD
        uart_tx_pad     : out   std_logic;
        ps2_clk_pad     : inout std_logic;
        ps2_data_pad    : inout std_logic;
        spi_cs_n_pad    : out   std_logic;
        spi_sdi_pad     : inout std_logic;
        spi_sdo_pad     : inout std_logic;
        spi_wp_n_pad    : inout std_logic;
        spi_hld_n_pad   : inout std_logic
    );
end entity basys3;

architecture rtl of basys3 is

    signal clk_100m00   : std_logic;
    signal slider_sw    : std_logic_vector(15 downto 0);
    signal led          : std_logic_vector(15 downto 0);
    signal seg          : std_logic_vector(6 downto 0);
    signal digit_en     : std_logic_vector(3 downto 0);
    signal dp           : std_logic;
    signal btn          : std_logic_vector(4 downto 0);
    signal pmod_jxadc   : std_logic_vector(3 downto 0);
    signal vga_red      : std_logic_vector(3 downto 0);
    signal vga_blue     : std_logic_vector(3 downto 0);
    signal vga_green    : std_logic_vector(3 downto 0);
    signal vga_hsync    : std_logic;
    signal vga_vsync    : std_logic;
    signal uart_rx      : std_logic;
    signal uart_tx      : std_logic;
    signal ps2_clk_i    : std_logic;
    signal ps2_clk_o    : std_logic;
    signal ps2_clk_t    : std_logic;
    signal ps2_data_i   : std_logic;
    signal ps2_data_o   : std_logic;
    signal ps2_data_t   : std_logic;
    signal spi_cs_n     : std_logic;
    signal spi_sdi_i    : std_logic;
    signal spi_sdi_o    : std_logic;
    signal spi_sdi_t    : std_logic;
    signal spi_sdo_i    : std_logic;
    signal spi_sdo_o    : std_logic;
    signal spi_sdo_t    : std_logic;
    signal spi_wp_n_i   : std_logic;
    signal spi_wp_n_o   : std_logic;
    signal spi_wp_n_t   : std_logic;
    signal spi_hld_n_i  : std_logic;
    signal spi_hld_n_o  : std_logic;
    signal spi_hld_n_t  : std_logic;

begin

    basys3_io_i0 : entity work.basys3_io
    -- generic map (
    -- )
    port map (
        clk_100m00_pad  => clk_100m00_pad,
        clk_100m00      => clk_100m00,
        slider_sw_pad   => slider_sw_pad,
        slider_sw       => slider_sw,
        led_pad         => led_pad,
        led             => led,
        seg_pad         => seg_pad,
        seg             => seg,
        digit_en_pad    => digit_en_pad,
        digit_en        => digit_en,
        dp_pad          => dp_pad,
        dp              => dp,
        btn_pad         => btn_pad,
        btn             => btn,
        pmod_jxadc_p    => pmod_jxadc_p,
        pmod_jxadc_n    => pmod_jxadc_n,
        pmod_jxadc      => pmod_jxadc,
        vga_red_pad     => vga_red_pad,
        vga_red         => vga_red,
        vga_blue_pad    => vga_blue_pad,
        vga_blue        => vga_blue,
        vga_green_pad   => vga_green_pad,
        vga_green       => vga_green,
        vga_hsync_pad   => vga_hsync_pad,
        vga_hsync       => vga_hsync,
        vga_vsync_pad   => vga_vsync_pad,
        vga_vsync       => vga_vsync,
        uart_rx_pad     => uart_rx_pad,
        uart_rx         => uart_rx,
        uart_tx_pad     => uart_tx_pad,
        uart_tx         => uart_tx,
        ps2_clk_pad     => ps2_clk_pad,
        ps2_clk_i       => ps2_clk_i,
        ps2_clk_o       => ps2_clk_o,
        ps2_clk_t       => ps2_clk_t,
        ps2_data_pad    => ps2_data_pad,
        ps2_data_i      => ps2_data_i,
        ps2_data_o      => ps2_data_o,
        ps2_data_t      => ps2_data_t,
        spi_cs_n_pad    => spi_cs_n_pad,
        spi_cs_n        => spi_cs_n,
        spi_sdi_pad     => spi_sdi_pad,
        spi_sdi_i       => spi_sdi_i,
        spi_sdi_o       => spi_sdi_o,
        spi_sdi_t       => spi_sdi_t,
        spi_sdo_pad     => spi_sdo_pad,
        spi_sdo_i       => spi_sdo_i,
        spi_sdo_o       => spi_sdo_o,
        spi_sdo_t       => spi_sdo_t,
        spi_wp_n_pad    => spi_wp_n_pad,
        spi_wp_n_i      => spi_wp_n_i,
        spi_wp_n_o      => spi_wp_n_o,
        spi_wp_n_t      => spi_wp_n_t,
        spi_hld_n_pad   => spi_hld_n_pad,
        spi_hld_n_i     => spi_hld_n_i,
        spi_hld_n_o     => spi_hld_n_o,
        spi_hld_n_t     => spi_hld_n_t
    );

end architecture rtl;
