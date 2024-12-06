export interface GPU {
  id: number;
  name: string;
  manufacturer: string;
  memorySize: number;
  memoryType: string;
  baseClockSpeed: number;
  boostClockSpeed: number;
  tdp: number;
  score: number;
}