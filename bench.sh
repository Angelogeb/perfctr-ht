#!/bin/bash

wait_if_skipped() {
  while ps -e | grep likwid
  do
    sleep 3
  done
}

groups=$(./bin/likwid-perfctr -a | tail -n +3 | cut -b 1-15)
groups=($groups)
group_flags="-g UOPS_RETIRE -g L3 -g DATA -g FLOPS_AVX -g L2CACHE -g CYCLE_ACTIVITY -g TLB_INSTR -g MEM -g MEM_DP -g FLOPS_DP -g UOPS -g TLB_DATA -g CLOCK -g L2 -g MEM_SP -g ENERGY -g ICACHE -g BRANCH -g RECOVERY -g DIVIDE -g UOPS_EXEC -g L3CACHE -g FLOPS_SP -g FALSE_SHARE -g TMA -g UOPS_ISSUE -g CYCLE_STALLS"
flags="-T 100ms"
command="./bin/likwid-perfctr $group_flags $flags"

# Disable Turbo Boost
./bin/likwid-setFrequencies -t 0

for f in 1.0 1.5 2.2; do
  ./bin/likwid-setFrequencies -y $f

  for t in 1 2; do
    # Set cpus to pin
    if [ $t -eq 1 ]
    then 
      cpus="-C 0"
    else
      cpus="-C 0,6"
    fi

    echo "$(date): FPU core bound $t - $f"
    $command -o data_aggregated/FPU-core-$t-$f.csv $cpus ./bin/likwid-bench -t ddot_sp -w S0:16kB:$t -i 15000000 > "data_aggregated/FPU-core-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): FPU mem bound $t - $f"
    $command -o data_aggregated/FPU-mem-$t-$f.csv $cpus ./bin/likwid-bench -t ddot_sp -w S0:1GB:$t -i 200 > "data_aggregated/FPU-mem-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): Copy cache $t - $f"
    $command -o data_aggregated/Copy-cache-$t-$f.csv $cpus ./bin/likwid-bench -t copy -w S0:16kB:$t -i 30000000 > "data_aggregated/Copy-cache-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): Copy mem $t - $f"
    $command -o data_aggregated/Copy-mem-$t-$f.csv $cpus ./bin/likwid-bench -t copy -w S0:1GB:$t -i 250 > "data_aggregated/Copy-mem-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): ALU core bound $t - $f"
    $command -o data_aggregated/ALU-core-$t-$f.csv $cpus ./bin/likwid-bench -t sum_int -w S0:16kB:$t -i 10000000 > "data_aggregated/ALU-core-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): ALU mem bound $t - $f"
    $command -o data_aggregated/ALU-mem-$t-$f.csv $cpus ./bin/likwid-bench -t sum_int -w S0:1GB:$t -i 150 > "data_aggregated/ALU-mem-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): AVX $t - $f"
    $command -o data_aggregated/AVX-cache-$t-$f.csv $cpus ./bin/likwid-bench -t ddot_sp_avx -w S0:16kB:$t -i 75000000 > "data_aggregated/AVX-cache-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

    echo "$(date): Scattered $t - $f"
    $command -o data_aggregated/Scattered-$t-$f.csv $cpus ./bin/likwid-bench -t copy_scattered -w S0:1GB:$t -i 50000 > "data_aggregated/Scattered-$t-$f.stdout"
    echo $(ps -e | grep likwid)
    wait_if_skipped

  done;
done