import React from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { GPU } from '../types/gpu';

interface GPUTableProps {
  data: GPU[];
}

export const GPUTable: React.FC<GPUTableProps> = ({ data }) => {
  return (
    <TableContainer component={Paper} sx={{ maxWidth: 1200, width: '100%', boxShadow: 3 }}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
            <TableCell><Typography variant="subtitle2">GPU Name</Typography></TableCell>
            <TableCell><Typography variant="subtitle2">Manufacturer</Typography></TableCell>
            <TableCell align="right"><Typography variant="subtitle2">Memory (GB)</Typography></TableCell>
            <TableCell><Typography variant="subtitle2">Memory Type</Typography></TableCell>
            <TableCell align="right"><Typography variant="subtitle2">Base Clock (MHz)</Typography></TableCell>
            <TableCell align="right"><Typography variant="subtitle2">Boost Clock (MHz)</Typography></TableCell>
            <TableCell align="right"><Typography variant="subtitle2">TDP (W)</Typography></TableCell>
            <TableCell align="right"><Typography variant="subtitle2">Score</Typography></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((gpu) => (
            <TableRow
              key={gpu.id}
              sx={{ '&:hover': { backgroundColor: '#f8f9fa' } }}
            >
              <TableCell component="th" scope="row">
                <Typography variant="body2" fontWeight="medium">{gpu.name}</Typography>
              </TableCell>
              <TableCell><Typography variant="body2">{gpu.manufacturer}</Typography></TableCell>
              <TableCell align="right"><Typography variant="body2">{gpu.memorySize}</Typography></TableCell>
              <TableCell><Typography variant="body2">{gpu.memoryType}</Typography></TableCell>
              <TableCell align="right"><Typography variant="body2">{gpu.baseClockSpeed}</Typography></TableCell>
              <TableCell align="right"><Typography variant="body2">{gpu.boostClockSpeed}</Typography></TableCell>
              <TableCell align="right"><Typography variant="body2">{gpu.tdp}</Typography></TableCell>
              <TableCell align="right"><Typography variant="body2">{gpu.score.toLocaleString()}</Typography></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};