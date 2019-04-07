#!/bin/bash

groups=$(./bin/likwid-perfctr -a | tail -n +3 | cut -b 1-15)
groups=($groups)
group_flags="-g UOPS_RETIRE -g L3 -g DATA -g FLOPS_AVX -g L2CACHE -g CYCLE_ACTIVITY -g TLB_INSTR -g MEM -g MEM_DP -g FLOPS_DP -g UOPS -g TLB_DATA -g CLOCK -g L2 -g MEM_SP -g ENERGY -g ICACHE -g BRANCH -g RECOVERY -g DIVIDE -g UOPS_EXEC -g L3CACHE -g FLOPS_SP -g FALSE_SHARE -g TMA -g UOPS_ISSUE -g CYCLE_STALLS"
flags="-T 100ms"
command="./bin/likwid-perfctr $group_flags $flags"

# Disable Turbo Boost
./bin/likwid-setFrequencies -t 0

for f in 1.2 1.7 2.2; do
  ./bin/likwid-setFrequencies -y $f

  for t in 1 2; do
    # Set cpus to pin
    if [ $t -eq 1 ]
    then 
      ht=""
      cpus="-C 0"
    else
      ht="-HT"
      cpus="-C 0,6"
    fi

    echo "$(date): FPU core bound $t - $f"
    $command -o data_aggregated/FPU-core-1$ht-$f.csv $cpus ./bin/likwid-bench -t ddot_sp -w S0:16kB:$t -i 90000000 > "data_aggregated/FPU-core-1$ht-$f.stdout"

    echo "$(date): FPU mem bound $t - $f"
    $command -o data_aggregated/FPU-mem-1$ht-$f.csv $cpus ./bin/likwid-bench -t ddot_sp -w S0:1GB:$t -i 1200 > "data_aggregated/FPU-mem-1$ht-$f.stdout"

    echo "$(date): Copy cache $t - $f"
    $command -o data_aggregated/Copy-cache-1$ht-$f.csv $cpus ./bin/likwid-bench -t copy -w S0:16kB:$t -i 180000000 > "data_aggregated/Copy-cache-1$ht-$f.stdout"

    echo "$(date): Copy mem $t - $f"
    $command -o data_aggregated/Copy-mem-1$ht-$f.csv $cpus ./bin/likwid-bench -t copy -w S0:1GB:$t -i 1500 > "data_aggregated/Copy-mem-1$ht-$f.stdout"

    echo "$(date): ALU core bound $t - $f"
    $command -o data_aggregated/ALU-core-1$ht-$f.csv $cpus ./bin/likwid-bench -t sum_int -w S0:16kB:$t -i 60000000 > "data_aggregated/ALU-core-1$ht-$f.stdout"

    echo "$(date): ALU mem bound $t - $f"
    $command -o data_aggregated/ALU-mem-1$ht-$f.csv $cpus ./bin/likwid-bench -t sum_int -w S0:1GB:$t -i 900 > "data_aggregated/ALU-mem-1$ht-$f.stdout"

    echo "$(date): AVX $t - $f"
    $command -o data_aggregated/AVX-cache-1$ht-$f.csv $cpus ./bin/likwid-bench -t ddot_sp_avx -w S0:16kB:$t -i 450000000 > "data_aggregated/AVX-cache-1$ht-$f.stdout"

    echo "$(date): Scattered $t - $f"
    $command -o data_aggregated/Scattered-mem-1$ht-$f.csv $cpus ./bin/likwid-bench -t copy_scattered -w S0:1GB:$t -i 300000 > "data_aggregated/Scattered-mem-1$ht-$f.stdout"

  done;
done