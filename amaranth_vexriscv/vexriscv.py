import enum
from pathlib import Path

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils import bits_for

from amaranth_soc import wishbone


__all__ = ["VexRiscvConfig", "VexRiscv"]


class VexRiscvConfig(enum.Enum):
    LITE            = "Lite"
    LITE_DEBUG      = "LiteDebug"
    LINUX_MPW_5     = "LinuxMPW5"
    LINUX_MPW_5L    = "LinuxMPW5L"
    LINUX_MPW_CACHE = "LinuxMPWCache"

    def with_debug_plugin(self):
        return self != self.LITE


class VexRiscv(wiring.Component):
    def __init__(self, *, config="LiteDebug", reset_vector=0x00100000):
        if not isinstance(reset_vector, int) or reset_vector < 0:
            raise TypeError(f"Reset vector address must be a non-negative integer, not "
                            f"{reset_vector!r}")
        if bits_for(reset_vector) > 32:
            raise ValueError(f"Reset vector address {reset_vector:#x} cannot be represented as a "
                             f"32-bit integer")

        self._config       = VexRiscvConfig(config)
        self._reset_vector = reset_vector

        super().__init__({
            "ibus": Out(wishbone.Signature(addr_width=30, data_width=32, granularity=8,
                                           features=("err", "cti", "bte"))),
            "dbus": Out(wishbone.Signature(addr_width=30, data_width=32, granularity=8,
                                           features=("err", "cti", "bte"))),

            "timer_irq":     In(unsigned(1)),
            "software_irq":  In(unsigned(1)),
            "external_irqs": In(unsigned(32)),

            "debug_rst_in":  In(unsigned(1)),
            "debug_rst_out": Out(unsigned(1)),

            "jtag_tms": In(unsigned(1)),
            "jtag_tdi": In(unsigned(1)),
            "jtag_tdo": Out(unsigned(1)),
            "jtag_tck": In(unsigned(1)),
        })

    @property
    def config(self):
        return self._config

    @property
    def reset_vector(self):
        return self._reset_vector

    def elaborate(self, platform):
        m = Module()

        instance_kwargs = {
            "i_clk": ClockSignal(),
            "i_reset": ResetSignal(),
            "i_externalResetVector": Const(self.reset_vector, unsigned(32)),

            "o_iBusWishbone_CYC": self.ibus.cyc,
            "o_iBusWishbone_STB": self.ibus.stb,
            "i_iBusWishbone_ACK": self.ibus.ack,
            "o_iBusWishbone_WE": self.ibus.we,
            "o_iBusWishbone_ADR": self.ibus.adr,
            "i_iBusWishbone_DAT_MISO": self.ibus.dat_r,
            "o_iBusWishbone_DAT_MOSI": self.ibus.dat_w,
            "o_iBusWishbone_SEL": self.ibus.sel,
            "i_iBusWishbone_ERR": self.ibus.err,
            "o_iBusWishbone_CTI": self.ibus.cti,
            "o_iBusWishbone_BTE": self.ibus.bte,

            "o_dBusWishbone_CYC": self.dbus.cyc,
            "o_dBusWishbone_STB": self.dbus.stb,
            "i_dBusWishbone_ACK": self.dbus.ack,
            "o_dBusWishbone_WE": self.dbus.we,
            "o_dBusWishbone_ADR": self.dbus.adr,
            "i_dBusWishbone_DAT_MISO": self.dbus.dat_r,
            "o_dBusWishbone_DAT_MOSI": self.dbus.dat_w,
            "o_dBusWishbone_SEL": self.dbus.sel,
            "i_dBusWishbone_ERR": self.dbus.err,
            "o_dBusWishbone_CTI": self.dbus.cti,
            "o_dBusWishbone_BTE": self.dbus.bte,

            "i_timerInterrupt": self.timer_irq,
            "i_softwareInterrupt": self.software_irq,
            "i_externalInterruptArray": self.external_irqs,
        }

        if self.config.with_debug_plugin():
            instance_kwargs.update({
                "i_debugReset": self.debug_rst_in,
                "o_debug_resetOut": self.debug_rst_out,

                "i_jtag_tms": self.jtag_tms,
                "i_jtag_tdi": self.jtag_tdi,
                "o_jtag_tdo": self.jtag_tdo,
                "i_jtag_tck": self.jtag_tck,
            })

        m.submodules.vexriscv = Instance("VexRiscv", **instance_kwargs)

        path = Path(__file__).parent / f"verilog/VexRiscv_{self.config.value}.v"
        with open(path, 'r') as f:
            platform.add_file(path.name, f)

        return m
