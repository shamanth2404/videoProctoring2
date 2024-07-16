// import React, { useState } from 'react';
// import Webcam from 'react-webcam';
// import './weblivecapture.css';

// const videoConstraints = {
// 	width: 1280,
// 	height: 720,
// 	facingMode: 'user'
// };

// const WebLiveCapture = () => {
// 	const webcamRef = React.useRef(null);
// 	const [ image, setImage ] = useState('');
// 	const capture = React.useCallback(
// 		() => {
// 			const imageSrc = webcamRef.current.getScreenshot();
// 			setImage(imageSrc);
// 			// console.log('Captured');
// 		},
// 		[ webcamRef ]
// 	);

// 	return (
// 		<React.Fragment>
// 			<Webcam
// 				audio={false}
// 				ref={webcamRef}
// 				screenshotFormat="image/jpeg"
// 				height={150}
// 				width={300}
// 				videoConstraints={videoConstraints}
// 			/>

// 			<button className="hide" onClick={capture}>
// 				Capture photo
// 			</button>
// 		</React.Fragment>
// 	);
// };

// export default WebLiveCapture;

import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import "./weblivecapture.css";
import axios from "axios";

const videoConstraints = {
  width: 1280,
  height: 720,
  facingMode: "user",
};

const WebLiveCapture = ({onWarning}) => {
  const webcamRef = useRef(null);
  const [image, setImage] = useState("");  
  const [isPaused,setIsPaused] = useState(false);

  const routes = [
    "http://localhost:8080/eye_tracking",    
    "http://localhost:8080/phone_tracking",
    "http://localhost:8080/hand_tracking",
    "http://localhost:8080/mouth_tracking",    
    "http://localhost:8080/headposing_tracking",    
  ]

  const capture = React.useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
    sendImage(imageSrc); // Send captured image to backend
  }, [webcamRef]);



  // const sendImage = async (imageSrc) => {
  //   if(!isPaused) {
  //     try {
  //       const response = await axios.post(
  //         "http://localhost:8080/headposing_tracking",
  //         {
  //           img: imageSrc,
  //           email: localStorage.getItem("email")
  //         }
  //       );
  //       console.log(response.data);
  //       if(response.data.warning){
  //         onWarning(response.data.warning,localStorage.getItem("warningCount"));
  //         setIsPaused(true);
  //         setTimeout(() => {
  //           setIsPaused(false);
  //         }, 10000);
  //       }	        
  //     } catch (error) {
  //       console.error("Error sending image:", error);
  //     }
  //   }
  // };

  const sendImage = async (imageSrc) => {
    if (!isPaused) {
      try {
        const requests = routes.map(route =>
          axios.post(route, { img: imageSrc,email: localStorage.getItem("email") })
        );

        const responses = await Promise.all(requests);
        
        responses.forEach(response => {
          console.log(response.data);
          if (response.data.warning) {
            onWarning(response.data.warning);
            setIsPaused(true);
            setTimeout(() => {
              setIsPaused(false);
            }, 10000);
          }
        });

      } catch (error) {
        console.error("Error sending image:", error);
      }
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      capture();
    }, 20000); // Capture and send image every second

    return () => clearInterval(interval);
  }, [capture]);

  return (
    <React.Fragment>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        height={150}
        width={300}
        videoConstraints={videoConstraints}
      />	        
    </React.Fragment>
  );
};

export default WebLiveCapture;
