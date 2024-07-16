import React from 'react';
import './terminated.css';

const Terminated = ({
	item
}) => {
	return (
		<div className="terminated">
			<div className="terminated-details">				
				<h4 className="warning-cnt">Warnings: {item.warningCount}</h4>
				<h4 className="message">Message: {item.warningType}</h4>
			</div>
			
		</div>
	);
};

export default Terminated;
