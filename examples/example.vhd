library ieee;
use ieee.std_logic_1164.all;

entity example is
    port (
        -- 125 MHz system clock input
        sys_clk_pad  : in    std_logic;

        -- User LED outputs
        led_pad      : out   std_logic_vector(3 downto 0);

        -- 200 MHz differential reference clock input
        ref_clk_p    : in    std_logic;
        ref_clk_n    : in    std_logic;

        -- LVDS serial data outputs
        lvds_data_p  : out   std_logic_vector(2 downto 0);
        lvds_data_n  : out   std_logic_vector(2 downto 0);

        -- General purpose IO
        gpio_pad     : inout std_logic_vector(4 downto 0);

        -- SerDes receive differential inputs
        serdes_rx_p  : in    std_logic_vector(3 downto 0);
        serdes_rx_n  : in    std_logic_vector(3 downto 0)
    );
end entity example;

architecture rtl of example is

    -- 125 MHz system clock input
    signal sys_clk      : std_logic;

    -- User LED outputs
    signal led          : std_logic_vector(3 downto 0);

    -- 200 MHz differential reference clock input
    signal ref_clk      : std_logic;

    -- LVDS serial data outputs
    signal lvds_data    : std_logic_vector(2 downto 0);

    -- General purpose IO
    signal gpio_i       : std_logic_vector(4 downto 0);
    signal gpio_o       : std_logic_vector(4 downto 0);
    signal gpio_t       : std_logic_vector(4 downto 0);

    -- SerDes receive differential inputs
    signal serdes_rx    : std_logic_vector(3 downto 0);

begin

    u_example_io : entity work.example_io
        port map (
            sys_clk_pad  => sys_clk_pad,
            sys_clk      => sys_clk,

            led_pad      => led_pad,
            led          => led,

            ref_clk_p    => ref_clk_p,
            ref_clk_n    => ref_clk_n,
            ref_clk      => ref_clk,

            lvds_data_p  => lvds_data_p,
            lvds_data_n  => lvds_data_n,
            lvds_data    => lvds_data,

            gpio_pad     => gpio_pad,
            gpio_i       => gpio_i,
            gpio_o       => gpio_o,
            gpio_t       => gpio_t,

            serdes_rx_p  => serdes_rx_p,
            serdes_rx_n  => serdes_rx_n,
            serdes_rx    => serdes_rx
        );

end architecture rtl;
