SRC := ${shell find . -type f -name \*.scala}

all: VexRiscv_Lite.v VexRiscv_LiteDebug.v VexRiscv_LinuxMPW5.v VexRiscv_LinuxMPW5L.v VexRiscv_LinuxMPWCache.v

VexRiscv_Lite.v: $(SRC)
	sbt compile "runMain vexriscv.GenCoreDefault --mulDiv true --singleCycleMulDiv false  --outputFile VexRiscv_Lite"

VexRiscv_LiteDebug.v: $(SRC)
	sbt compile "runMain vexriscv.GenCoreDefault --mulDiv true --singleCycleMulDiv false -d --outputFile VexRiscv_LiteDebug"

VexRiscv_LinuxMPW5.v: $(SRC)
	sbt compile "runMain vexriscv.GenCoreDefault --iCacheSize 512 --dCacheSize 256 --mulDiv true --singleCycleMulDiv false --csrPluginConfig linux-minimal -d --outputFile VexRiscv_LinuxMPW5"

VexRiscv_LinuxMPW5L.v: $(SRC)
	sbt compile "runMain vexriscv.GenCoreDefault --iCacheSize 1024 --dCacheSize 512 --mulDiv true --csrPluginConfig linux-minimal -d --outputFile VexRiscv_LinuxMPW5L"

VexRiscv_LinuxMPWCache.v: $(SRC)
	sbt compile "runMain vexriscv.GenCoreDefault --iCacheSize 2048 --dCacheSize 1024 --mulDiv true --csrPluginConfig linux-minimal -d --outputFile VexRiscv_LinuxMPWCache"
