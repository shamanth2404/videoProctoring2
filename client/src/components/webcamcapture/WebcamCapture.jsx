import React, { useState } from 'react';
import Webcam from 'react-webcam';
import './webcamcapture.css';

const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: 'user'
};

const WebcamCapture = ({ setImage }) => {
    const webcamRef = React.useRef(null);
    const [image, setImageState] = useState('');

    const capture = React.useCallback(() => {
        const imageSrc = webcamRef.current.getScreenshot();
        setImageState(imageSrc);

        // Convert base64 string to a file
        fetch(imageSrc)
            .then(res => res.blob())
            .then(blob => {
                const file = new File([blob], "capturedImage.jpg", { type: "image/jpeg" });
                console.log(file)
                setImage(file);
            });
    }, [webcamRef, setImage]);

    return (
        <React.Fragment>
            {image === '' ? (
                <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    height={300}
                    width={450}
                    videoConstraints={videoConstraints}
                />
            ) : (
                <img className="captured" src={image} alt="captured" />
            )}

            {image === '' ? (
                <button type="button" onClick={capture}>Capture photo</button>
            ) : (
                <button type="button" className="proceed">Proceed</button>
            )}
        </React.Fragment>
    );
};

export default WebcamCapture;