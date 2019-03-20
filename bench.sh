#!/bin/bash

wait_if_skipped() {
  while ps -e | grep likwid
  do
    sleep 3
  done
}

groups=$(./bin/likwid-perfctr -a | tail -n +3 | cut -b 1-15)
groups=($groups)
group_flags=$(printf -- "-g %s " "${groups[@]}")
flags="-t 100ms"
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
    $command $cpus ./bin/likwid-bench -t ddot_sp -w S0:16kB:$t -i 15000000 > "data/FPU-core-$t-$f.stdout" 2> "data/FPU-core-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

    echo "$(date): FPU mem bound $t - $f"
    $command $cpus ./bin/likwid-bench -t ddot_sp -w S0:1GB:$t -i 200 > "data/FPU-mem-$t-$f.stdout" 2> "data/FPU-mem-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

    echo "$(date): Copy cache $t - $f"
    $command $cpus ./bin/likwid-bench -t copy -w S0:16kB:$t -i 30000000 > "data/Copy-cache-$t-$f.stdout" 2> "data/Copy-cache-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

    echo "$(date): Copy mem $t - $f"
    $command $cpus ./bin/likwid-bench -t copy -w S0:1GB:$t -i 250 > "data/Copy-mem-$t-$f.stdout" 2> "data/Copy-mem-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

    echo "$(date): ALU core bound $t - $f"
    $command $cpus ./bin/likwid-bench -t sum_int -w S0:16kB:$t -i 10000000 > "data/ALU-core-$t-$f.stdout" 2> "data/ALU-core-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

    echo "$(date): ALU mem bound $t - $f"
    $command $cpus ./bin/likwid-bench -t sum_int -w S0:1GB:$t -i 150 > "data/ALU-mem-$t-$f.stdout" 2> "data/ALU-mem-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

    echo "$(date): AVX $t - $f"
    $command $cpus ./bin/likwid-bench -t ddot_sp_avx -w S0:16kB:$t -i 75000000 > "data/AVX-cache-$t-$f.stdout" 2> "data/AVX-cache-$t-$f.stderr"
    echo $(ps -e | rg likwid)
    wait_if_skipped

  done;
done