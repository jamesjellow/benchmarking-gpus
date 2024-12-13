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
	LinearProgress,
	Box,
} from '@mui/material';
import { FeatureImportance } from '../types/feature';

interface FeatureTableProps {
	data: FeatureImportance[];
}

export const FeatureTable: React.FC<FeatureTableProps> = ({ data }) => {
	const maxImportance = Math.max(...data.map((item) => item.Importance));

	return (
		<TableContainer
			component={Paper}
			sx={{ maxWidth: 800, width: '100%', boxShadow: 3 }}
		>
			<Table>
				<TableHead>
					<TableRow sx={{ backgroundColor: '#f5f5f5' }}>
						<TableCell width="50%">
							<Typography variant="subtitle2">Feature</Typography>
						</TableCell>
						<TableCell width="50%">
							<Typography variant="subtitle2">Importance</Typography>
						</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{data.map((item) => (
						<TableRow
							key={item.Feature}
							sx={{ '&:hover': { backgroundColor: '#f8f9fa' } }}
						>
							<TableCell>
								<Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
									{item.Feature}
								</Typography>
							</TableCell>
							<TableCell>
								<Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
									<LinearProgress
										variant="determinate"
										value={(item.Importance / maxImportance) * 100}
										sx={{
											width: '100%',
											height: 8,
											borderRadius: 1,
											backgroundColor: '#e9ecef',
											'& .MuiLinearProgress-bar': {
												backgroundColor: '#2196f3',
												borderRadius: 1,
											},
										}}
									/>
									<Typography variant="body2" sx={{ minWidth: '45px' }}>
										{Math.floor(item.Importance * 100)}%
									</Typography>
								</Box>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</TableContainer>
	);
};
