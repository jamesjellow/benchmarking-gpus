import { GPU } from '../types/gpu';

export const gpuData: GPU[] = [
  {
    id: 1,
    name: "RTX 4090",
    manufacturer: "NVIDIA",
    memorySize: 24,
    memoryType: "GDDR6X",
    baseClockSpeed: 2235,
    boostClockSpeed: 2520,
    tdp: 450,
    score: 38000
  },
  {
    id: 2,
    name: "RX 7900 XTX",
    manufacturer: "AMD",
    memorySize: 24,
    memoryType: "GDDR6",
    baseClockSpeed: 2300,
    boostClockSpeed: 2500,
    tdp: 355,
    score: 32000
  },
  {
    id: 3,
    name: "RTX 4080",
    manufacturer: "NVIDIA",
    memorySize: 16,
    memoryType: "GDDR6X",
    baseClockSpeed: 2205,
    boostClockSpeed: 2505,
    tdp: 320,
    score: 29000
  },
  {
    id: 4,
    name: "RX 7900 XT",
    manufacturer: "AMD",
    memorySize: 20,
    memoryType: "GDDR6",
    baseClockSpeed: 2000,
    boostClockSpeed: 2400,
    tdp: 315,
    score: 27500
  },
  {
    id: 5,
    name: "RTX 4070 Ti",
    manufacturer: "NVIDIA",
    memorySize: 12,
    memoryType: "GDDR6X",
    baseClockSpeed: 2310,
    boostClockSpeed: 2610,
    tdp: 285,
    score: 25000
  }
];