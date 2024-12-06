import { Container, Typography, Box, Button } from '@mui/material';
import { BarChart2, Github } from 'lucide-react';
import { FeatureTable } from './components/FeatureTable';
import { featureData } from './data/featureData';

function App() {
	return (
		<Container
			maxWidth={false}
			sx={{
				minHeight: '100vh',
				backgroundColor: '#f8f9fa',
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'center',
				py: 4,
				gap: 3,
			}}
		>
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					gap: 1,
				}}
			>
				<Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
					<BarChart2 size={32} />
					<Typography variant="h4" component="h1" fontWeight="bold">
						GPU Feature Importance
					</Typography>
				</Box>
				<Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
					Top-N Metrics for GPU Performance Analysis
				</Typography>
				<Typography
					variant="caption"
					color="text.secondary"
					sx={{
						backgroundColor: '#e9ecef',
						px: 2,
						py: 1,
						borderRadius: 1,
						mb: 3,
					}}
				>
					⚡ This analysis updates every 30 minutes
				</Typography>
			</Box>

			<FeatureTable data={featureData} />

			<Button
				variant="contained"
				href="https://github.com/jamesjellow/benchmarking-gpus/tree/main"
				target="_blank"
				rel="noopener noreferrer"
				startIcon={<Github size={20} />}
				sx={{
					mt: 3,
					backgroundColor: '#24292e',
					'&:hover': {
						backgroundColor: '#1b1f23',
					},
					textTransform: 'none',
					px: 4,
					py: 1,
				}}
			>
				Contribute
			</Button>
		</Container>
	);
}

export default App;
