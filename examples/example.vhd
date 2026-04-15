library ieee;
use ieee.std_logic_1164.all;

entity example is
    -- generic (
    -- )
    port (
        -- 125 MHz system clock input
        sys_clk_pad     : in    std_logic;
        -- User LED outputs
        led_pad         : out   std_logic_vector(3 downto 0);
        -- User LED output, buffer inferred
        user_led_pad    : out   std_logic;
        -- 200 MHz differential reference clock input
        ref_clk_p       : in    std_logic;
        ref_clk_n       : in    std_logic;
        -- LVDS serial data outputs
        lvds_data_p     : out   std_logic_vector(2 downto 0);
        lvds_data_n     : out   std_logic_vector(2 downto 0);
        -- General purpose IO
        gpio_pad        : inout std_logic_vector(4 downto 0);
        -- Spare output, driven directly
        spare_pad       : out   std_logic;
        -- Differential general IO
        diff_io_p       : inout std_logic;
        diff_io_n       : inout std_logic
    );
end entity example;

architecture rtl of example is

    signal sys_clk      : std_logic;
    signal led          : std_logic_vector(3 downto 0);
    signal user_led     : std_logic;
    signal ref_clk      : std_logic;
    signal lvds_data    : std_logic_vector(2 downto 0);
    signal gpio_i       : std_logic_vector(4 downto 0);
    signal gpio_o       : std_logic_vector(4 downto 0);
    signal gpio_t       : std_logic_vector(4 downto 0);
    signal diff_io_i    : std_logic;
    signal diff_io_o    : std_logic;
    signal diff_io_t    : std_logic;

begin

    example_io_i0 : entity work.example_io
    -- generic map (
    -- )
    port map (
        sys_clk_pad     => sys_clk_pad,
        sys_clk         => sys_clk,
        led_pad         => led_pad,
        led             => led,
        user_led_pad    => user_led_pad,
        user_led        => user_led,
        ref_clk_p       => ref_clk_p,
        ref_clk_n       => ref_clk_n,
        ref_clk         => ref_clk,
        lvds_data_p     => lvds_data_p,
        lvds_data_n     => lvds_data_n,
        lvds_data       => lvds_data,
        gpio_pad        => gpio_pad,
        gpio_i          => gpio_i,
        gpio_o          => gpio_o,
        gpio_t          => gpio_t,
        diff_io_p       => diff_io_p,
        diff_io_n       => diff_io_n,
        diff_io_i       => diff_io_i,
        diff_io_o       => diff_io_o,
        diff_io_t       => diff_io_t
    );

end architecture rtl;
