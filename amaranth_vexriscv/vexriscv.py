from amaranth import *
from amaranth.utils import log2_int

from amaranth_soc import wishbone

from pathlib import Path

class VexRiscv(Elaboratable):
    def __init__(self, config="LiteDebug", reset_vector=0x00100000):
        self.config = config
        self.dbus = wishbone.Interface(addr_width=30,
                                      data_width=32, granularity=8, features={"cti", "bte"}) 
        self.ibus = wishbone.Interface(addr_width=30,
                                      data_width=32, granularity=8, features={"cti", "bte"})
        self.timer_irq = Signal()
        self.software_irq = Signal()
        self.irq_sigs = [None for i in range(32)]
        self.debug_rst_out = Signal()
        self.debug_rst_in = None
        self.jtag_tms = Signal()
        self.jtag_tdi = Signal()
        self.jtag_tdo = Signal()
        self.jtag_tck = Signal()
        self.reset_vector = reset_vector

    def add_irq(self, irq, sig):
        assert self.irq_sigs[irq] is None
        self.irq_sigs[irq] = sig

    def elaborate(self, platform):
        m = Module()
        ext_irq = Signal(32)
        for i, irq in enumerate(self.irq_sigs):
            if irq is not None:
                m.d.comb += ext_irq[i].eq(irq)
            else:
                m.d.comb += ext_irq[i].eq(0)
        conn = dict(
            i_timerInterrupt=self.timer_irq,
            i_softwareInterrupt=self.software_irq,
            i_externalInterruptArray=ext_irq,
            o_debug_resetOut=self.debug_rst_out,

            o_iBusWishbone_CYC=self.ibus.cyc,
            o_iBusWishbone_STB=self.ibus.stb,
            i_iBusWishbone_ACK=self.ibus.ack,
            o_iBusWishbone_WE=self.ibus.we,
            o_iBusWishbone_ADR=self.ibus.adr,
            i_iBusWishbone_DAT_MISO=self.ibus.dat_r,
            o_iBusWishbone_DAT_MOSI=self.ibus.dat_w,
            o_iBusWishbone_SEL=self.ibus.sel,
            i_iBusWishbone_ERR=0,
            o_iBusWishbone_CTI=self.ibus.cti,
            o_iBusWishbone_BTE=self.ibus.bte,

            o_dBusWishbone_CYC=self.dbus.cyc,
            o_dBusWishbone_STB=self.dbus.stb,
            i_dBusWishbone_ACK=self.dbus.ack,
            o_dBusWishbone_WE=self.dbus.we,
            o_dBusWishbone_ADR=self.dbus.adr,
            i_dBusWishbone_DAT_MISO=self.dbus.dat_r,
            o_dBusWishbone_DAT_MOSI=self.dbus.dat_w,
            o_dBusWishbone_SEL=self.dbus.sel,
            i_dBusWishbone_ERR=0,
            o_dBusWishbone_CTI=self.dbus.cti,
            o_dBusWishbone_BTE=self.dbus.bte,

            i_clk=ClockSignal(),
            i_reset=ResetSignal(),
            i_externalResetVector=self.reset_vector,
        )
        if "Debug" in self.config or "LinuxMPW" in self.config:
            # Variants with JTAG
            conn["i_jtag_tms"] = self.jtag_tms
            conn["i_jtag_tdi"] = self.jtag_tdi
            conn["o_jtag_tdo"] = self.jtag_tdo
            conn["i_jtag_tck"] = self.jtag_tck
            conn["i_debugReset"] = ResetSignal() if self.debug_rst_in is None else self.debug_rst_in
            conn["o_debug_resetOut"] = self.debug_rst_out

        m.submodules.vex = Instance(
            "VexRiscv",
            **conn
        )
        filename = Path(__file__).parent / f"verilog/VexRiscv_{self.config}.v"
        with open(filename, 'r') as f:
            platform.add_file(str(filename), f)
        return m
