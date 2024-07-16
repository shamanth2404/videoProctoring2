import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import { CtaButton, Timer, WebLiveCapture } from "../../components";
import devtools from "devtools-detect";
import "./exam.css";


const Exam = () => {
  const navigate = useNavigate();
  const { formLinkCode } = useParams();
  const isAuthenticated = !!localStorage.getItem("token"); // Check if the user is authenticated
  const studentFullName = localStorage.getItem("fullName"); // Get the student's full name from local storage
  const studentEmail = localStorage.getItem("email"); // Get the student's email from local storage
  const [profilePicture, setProfilePicture] = useState(null); // State to store the profile picture
  const [examName, setExamName] = useState(""); // State to store the exam name
  const [duration, setDuration] = useState(60); // State to store the exam duration, default is 60
  const [testLink, setTestLink] = useState(""); // State to store the test link
  const [warningCnt, setWarningCnt] = useState(0); // State to count the warnings
  const [isDevToolsOpen, setIsDevToolsOpen] = useState(false); // State to track if devtools is open
  const [showMessage, setShowMessage] = useState(""); // State to store messages to show
  const intervalRefs = useRef([]); // Ref to store intervals for cleanup
  const [isBlurred, setIsBlurred] = useState(false);
  const [isResized, setIsResized] = useState(false);
  const [isProcessingWarning, setIsProcessingWarning] = useState(false);
  const [warningQueue, setWarningQueue] = useState(() => {
    const savedQueue = localStorage.getItem("warningQueue");
    return savedQueue ? JSON.parse(savedQueue) : [];
  });  
  const iframeRef = useRef(null);
  

  // Check if the user is authenticated when the component mounts
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login"); // Redirect to login if not authenticated
    }
  }, []);

  // Fetch test details and user details when the component mounts
  useEffect(() => {
    async function fetchTestDetails() {
      try {
        // Fetch test details from the backend
        const response = await axios.get(
          `http://localhost:5000/api/test-details/${formLinkCode}`
        );
        setTestLink(response.data.test_link_by_user); // Set the test link
        setExamName(response.data.test_name); 
        
      } catch (error) {
        console.error("Error fetching test details:", error);
        navigate("/login"); // Redirect to login on error
      }
    }

    async function fetchUserDetails() {
      try {
        // Fetch user details from the backend
        const response = await axios.get(
          `http://localhost:5000/api/user-details/${studentEmail}`
        );
        setProfilePicture(response.data.user.profilePicture); // Set the profile picture
        localStorage.setItem("fullName", response.data.user.fullName); // Store the full name in local storage
      } catch (error) {
        console.error("Error fetching user details:", error);
      }
    }

    fetchTestDetails(); // Call the function to fetch test details
    fetchUserDetails(); // Call the function to fetch user details
  }, [formLinkCode, navigate, studentEmail]);

  
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setShowMessage("Do not switch tabs or windows.");
        handleWarning("Do not switch tabs or windows");
      }
    };    

    const handleFocus = () => {
      handleWarning("focus on exam page");
    };

    const handleDevToolsChange = (event) => {
      event.preventDefault();
      if (event.detail.isOpen) {
        setIsDevToolsOpen(true);
        setShowMessage("Do not open the developer tools.");
        handleWarning("Do not open Dev tools");
      } else {
        setIsDevToolsOpen(false);
        setShowMessage("");
      }
    };

    const handleResize = () => {
      setShowMessage("Do not resize the window.");
      handleWarning("Do not resize windows.");
    };

    const handleContextMenu = (e) => {
      e.preventDefault();
      handleWarning("Do not right click");
    };
    // window.resizeTo(window.screen.width, window.screen.height);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("contextmenu", handleContextMenu);    
    document.addEventListener("focus", handleFocus);
    // window.addEventListener("devtoolschange", handleDevToolsChange);
    window.addEventListener("resize", handleResize);

    // Add a listener for devtools detection

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("contextmenu", handleContextMenu);      
      document.removeEventListener("focus", handleFocus);
      // window.removeEventListener("devtoolschange", handleDevToolsChange);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const startRecording = async () => {
    try {
      const res = await axios.post("http://localhost:8080/start-recording");
      console.log(res.data);
      const testCode = localStorage.getItem("testCode");
      const cheat = await axios.post(
        "http://localhost:8080/process-text",
        {testCode},
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      if (cheat.data.alert) {
        handleWarning(cheat.data.alert);
        //Add the audio to the database
      }
      console.log(cheat.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    // Set up the interval to call myFunction every 10 seconds (10000 ms)
    const intervalId = setInterval(startRecording, 20000);

    // Clean up the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const checkOpenWindows = async () => {
    const openWindows = await axios.get(
      `http://localhost:8080/window_tracking`
    );
    console.log(openWindows.data);
    if (openWindows.data.length > 0) {
      handleWarning("Multiple Windows Open");
    }
    const bluetooth = await axios.get(
      `http://localhost:8080/bluetooth/status`
    );
    console.log(bluetooth.data);
    if (bluetooth.data.bluetooth_on) {
      handleWarning("Bluetooth is On");
    }
    const usb = await axios.get(
      `http://localhost:8080/usb/devices`
    );
    console.log(usb.data);
    if (usb.data.usb_devices.length > 0) {
      handleWarning("USB devices Connected");
    }
  };

  useEffect(() => {
    // Set up the interval to call myFunction every 10 seconds (10000 ms)
    const intervalId = setInterval(checkOpenWindows, 20000);

    // Clean up the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to check for malpractice
 
  const handleFinish = (e) => {
    e.preventDefault();
    const userConfirmed = window.confirm("Did you submit the form?");
    if (userConfirmed) {
      window.location.href = "/";
    }
  };

  useEffect(() => {
    const handleBackButton = (e) => {
      e.preventDefault();
      window.history.pushState(null, null, window.location.pathname);
    };
    window.addEventListener("popstate", handleBackButton);

    const handleBeforeUnload = (e) => {
      e.preventDefault();
    };
    // window.addEventListener("beforeunload", handleBeforeUnload);

    window.history.pushState(null, null, window.location.pathname);

    return () => {
      window.removeEventListener("popstate", handleBackButton);
      // window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  const handleWarning = (warning) => {
    setWarningQueue((prevQueue) => {
      const newQueue = [...prevQueue, warning];
      localStorage.setItem("warningQueue", JSON.stringify(newQueue));
      return newQueue;
    });
  };

  const processWarnings = () => {
    if (warningQueue.length > 0) {
      const [currentWarning, ...remainingWarnings] = warningQueue;
      setWarningQueue(remainingWarnings);
      localStorage.setItem("warningQueue", JSON.stringify(remainingWarnings));
      console.log(localStorage.getItem("testCode"));
      const addWarning = axios.put("http://localhost:5000/api/add-warning", {
        email: localStorage.getItem("email"),
        testCode: localStorage.getItem("testCode"),
        warningType: currentWarning,
      });
      console.log(addWarning);
      displayWarning(currentWarning);
    }
  };

  const displayWarning = (warning) => {
    setIsProcessingWarning(true);
    localStorage.setItem("warning", warning); // Set warning message
    localStorage.setItem(
      "warningCount",
      (parseInt(localStorage.getItem("warningCount")) || 0) + 1
    ); // Set warning count
    setIsBlurred(true);
    setTimeout(() => {
      setIsBlurred(false);
      setIsProcessingWarning(false);
    }, 10000); // 10 seconds
  };

  useEffect(() => {
    processWarnings();
  }, [warningQueue]);

  const handleRightClick = (event) => {
    event.preventDefault();
    handleWarning("Do not right click");
  };  

  return (
    <div className="exam-container">
      <div className="left-column">
        <div className="image-capture">
          <WebLiveCapture onWarning={handleWarning} />{" "}
          {/* Component to capture live webcam feed */}
          {showMessage && <p>{showMessage}</p>}
          {/* <AudioRecorder /> */}
        </div>
        <div className="exam-details">
          <h3 className="title-heading">Student Details</h3>
          <div className="details">
            <h4 className="student-name">Student Name: {studentFullName}</h4>{" "}
            {/* Display student's full name */}
            <h4 className="student-email">
              Student Email: {studentEmail}
            </h4>{" "}
            {/* Display student's email */}
            {profilePicture && (
              <img
                src={`http://localhost:5000/public/${profilePicture}`}
                alt="Profile"
                className="profile-picture"
              /> // Display student's profile picture
            )}
          </div>
        </div>
      </div>

      <div className="embedded-form">
        {isBlurred && (
          <div className="disable">
            <h2> {localStorage.getItem("warning")}</h2> {/* Display messages */}
            <h2>Warnings: {localStorage.getItem("warningCount")}</h2>{" "}
            {/* Display warning count */}
          </div>
        )}
        <div className={isBlurred ? "form blur" : "form"} id="form-blur">
          <h2 className="title-heading">{examName}</h2>{" "}
          {/* Display exam name */}
          <div style={{ position: "relative", width: "90%" }}>
            {testLink ? (
              <>
                <iframe
                  onContextMenu={handleRightClick}
                  title={examName}
                  className="form-link disable-select"
                  src={testLink}
                  style={{ width: "100%", height: "500px", border: "none" }}
                >
                  Form
                </iframe>
              </>
            ) : (
              <p>Loading...</p>
            )}
          </div>
          <div className="responsive-message">
            <h1>Please join via a Laptop/PC for best performance</h1>
          </div>
        </div>
      </div>

      <div>
        <div className="timer">
        <Timer />
        {" "}
          {/* Display timer with duration from backend */}
        </div>
        <div onClick={handleFinish}>
          <CtaButton text="Finish" />
        </div>
      </div>
    </div>
  );
};

export default Exam;
