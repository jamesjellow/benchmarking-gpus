const AnimatedBarChart = ({ size = 50, color = 'currentColor' }) => {
	return (
		<svg
			width={size}
			height={size}
			viewBox="0 0 24 24"
			strokeWidth="2"
			stroke={color}
			fill="none"
			strokeLinecap="round"
			strokeLinejoin="round"
		>
			{/* Left bar */}
			<line x1="6" x2="6" y1="20" y2="14">
				<animate
					attributeName="y2"
					values="14;10;14"
					dur="1.5s"
					repeatCount="indefinite"
				/>
			</line>

			{/* Middle bar */}
			<line x1="12" x2="12" y1="20" y2="4">
				<animate
					attributeName="y2"
					values="4;8;4"
					dur="1.5s"
					repeatCount="indefinite"
				/>
			</line>

			{/* Right bar */}
			<line x1="18" x2="18" y1="20" y2="10">
				<animate
					attributeName="y2"
					values="10;6;10"
					dur="1.5s"
					repeatCount="indefinite"
				/>
			</line>
		</svg>
	);
};

export default AnimatedBarChart;
