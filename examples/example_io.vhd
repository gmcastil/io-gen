-- IO ring for example
-- Port naming convention:
--   Pad-side ports use _pad (single-ended), _p/_n (differential)
--   Fabric-side ports use the signal name directly for in/out signals
--   Fabric-side tristate signals use _i (read from pad), _o (drive to pad),
--   _t (tristate enable, active high = output disabled)
--   Note: IOBUF primitive port names are from the primitive perspective:
--     IOBUF I connects to gpio_o (fabric drives out)
--     IOBUF O connects to gpio_i (fabric reads in)
library ieee;
use ieee.std_logic_1164.all;

library unisim;
use unisim.vcomponents.all;

entity example_io is
    port (
        -- 125 MHz system clock input
        sys_clk_pad  : in    std_logic;
        sys_clk      : out   std_logic;

        -- User LED outputs
        led_pad      : out   std_logic_vector(3 downto 0);
        led          : in    std_logic_vector(3 downto 0);

        -- 200 MHz differential reference clock input
        ref_clk_p    : in    std_logic;
        ref_clk_n    : in    std_logic;
        ref_clk      : out   std_logic;

        -- LVDS serial data outputs
        lvds_data_p  : out   std_logic_vector(2 downto 0);
        lvds_data_n  : out   std_logic_vector(2 downto 0);
        lvds_data    : in    std_logic_vector(2 downto 0);

        -- General purpose IO
        gpio_pad     : inout std_logic_vector(4 downto 0);
        gpio_i       : out   std_logic_vector(4 downto 0);
        gpio_o       : in    std_logic_vector(4 downto 0);
        gpio_t       : in    std_logic_vector(4 downto 0)
    );
end entity example_io;

architecture rtl of example_io is
begin

    -- 125 MHz system clock input
    ibuf_sys_clk_i0 : IBUF
        port map (
            I => sys_clk_pad,
            O => sys_clk
        );

    -- User LED outputs
    obuf_led_i0 : OBUF
        port map (
            I => led(0),
            O => led_pad(0)
        );
    obuf_led_i1 : OBUF
        port map (
            I => led(1),
            O => led_pad(1)
        );
    obuf_led_i2 : OBUF
        port map (
            I => led(2),
            O => led_pad(2)
        );
    obuf_led_i3 : OBUF
        port map (
            I => led(3),
            O => led_pad(3)
        );

    -- 200 MHz differential reference clock input
    ibufds_ref_clk_i0 : IBUFDS
        port map (
            I  => ref_clk_p,
            IB => ref_clk_n,
            O  => ref_clk
        );

    -- LVDS serial data outputs
    obufds_lvds_data_i0 : OBUFDS
        port map (
            I  => lvds_data(0),
            O  => lvds_data_p(0),
            OB => lvds_data_n(0)
        );
    obufds_lvds_data_i1 : OBUFDS
        port map (
            I  => lvds_data(1),
            O  => lvds_data_p(1),
            OB => lvds_data_n(1)
        );
    obufds_lvds_data_i2 : OBUFDS
        port map (
            I  => lvds_data(2),
            O  => lvds_data_p(2),
            OB => lvds_data_n(2)
        );

    -- General purpose IO
    iobuf_gpio_i0 : IOBUF
        port map (
            IO => gpio_pad(0),
            I  => gpio_o(0),
            O  => gpio_i(0),
            T  => gpio_t(0)
        );
    iobuf_gpio_i1 : IOBUF
        port map (
            IO => gpio_pad(1),
            I  => gpio_o(1),
            O  => gpio_i(1),
            T  => gpio_t(1)
        );
    iobuf_gpio_i2 : IOBUF
        port map (
            IO => gpio_pad(2),
            I  => gpio_o(2),
            O  => gpio_i(2),
            T  => gpio_t(2)
        );
    iobuf_gpio_i3 : IOBUF
        port map (
            IO => gpio_pad(3),
            I  => gpio_o(3),
            O  => gpio_i(3),
            T  => gpio_t(3)
        );
    iobuf_gpio_i4 : IOBUF
        port map (
            IO => gpio_pad(4),
            I  => gpio_o(4),
            O  => gpio_i(4),
            T  => gpio_t(4)
        );

end architecture rtl;
