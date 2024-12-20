import { useState, useEffect } from 'react';
import axios from 'axios';
import {
	Container,
	Typography,
	Box,
	Button,
	CircularProgress,
} from '@mui/material';
import { Github } from 'lucide-react';
import { FeatureTable } from './components/FeatureTable';
import AnimatedBarChart from './components/AnimatedBartChart';

const App = () => {
	const [featureData, setFeatureData] = useState([]);
	const [loading, setLoading] = useState(false);

	const fetchData = () => {
		setLoading(true);
		const apiUrl = 'https://api.gpu-bench.com/v2/features';

		axios
			.get(apiUrl)
			.then((response) => {
				setFeatureData(response.data);
			})
			.catch((error) => {
				console.error('Error fetching data:', error);
			})
			.finally(() => {
				setLoading(false);
			});
	};

	useEffect(() => {
		// Fetch data on component mount
		fetchData();

		// Set interval to refetch data every 30 minutes (1800000 ms)
		const intervalId = setInterval(() => {
			fetchData();
		}, 1800000);

		// Clear interval on component unmount
		return () => clearInterval(intervalId);
	}, []);

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
					<AnimatedBarChart size={50} color="#8A2BE2" />
					<Typography
						variant="h4"
						component="h1"
						fontWeight="bold"
						sx={{
							background: 'linear-gradient(to right, #8A2BE2, #00BFFF)',
							WebkitBackgroundClip: 'text',
							WebkitTextFillColor: 'transparent',
							// Add optional shine effect by changing angle or colors if desired
						}}
					>
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
					⚡ This page updates every 30 minutes
				</Typography>
			</Box>

			{loading ? (
				<Box
					sx={{
						display: 'flex',
						justifyContent: 'center',
						alignItems: 'center',
						height: '200px',
					}}
				>
					<CircularProgress />
				</Box>
			) : (
				<FeatureTable data={featureData} />
			)}

			<Button
				variant="contained"
				href="https://github.com/jamesjellow/benchmarking-gpus/tree/main/inference/bert99"
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
};

export default App;
