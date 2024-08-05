import React, { useEffect, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { CtaButton, CommonInput, Navbar } from "../../components"; // Removed Navbar import
import infinite from "./../../assets/infinite.svg";
import "./landing.css";
import axios from "axios";

const featureList = [
  "Eye & Head Movements Detection",
  "Hand Gestures Detection",  
  "Multiple People Detection",
  "Voice Detection",
  "Devtools Check",
  "Full Screen Check",
  "Multiple Windows Check",
  "Bluetooth Connection Check",
];

const Landing = () => {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem("token");
  const testCodeRef = useRef(null);
  const [message, setMessage] = useState("");
  const [attemptMessage, setAttemptMessage] = useState("");
  const [windows, setWindows] = useState([]);
  const buttonRef = useRef(null);

   useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  const handleJoin = async (e) => {
    e.preventDefault();

    if (testCodeRef.current) {
      const testCode = testCodeRef.current.value;
      if (localStorage.getItem("role") === "Teacher") {
        setAttemptMessage("Teachers aren't allowed to join a test");
        return;
      }
      if (testCode) {
        try{

          setWindows([]);
          setAttemptMessage("Loading...")
        const email = localStorage.getItem("email");
        const response = await axios.get(
          `http://localhost:5000/api/attempted-test?email=${email}&testCode=${testCode}`
        );
        console.log(response.data);
        if (response.data.msg === "Test not found") {
          setAttemptMessage("Invalid Test code");
          return;
        }

        if (response.data.length === 0) {
          const testDetails = await axios.get(
            `http://localhost:5000/api/test-details/${testCode}`
          );
          console.log(testDetails.data);
          console.log(testDetails.data.start_time);
          const startTime = new Date(testDetails.data.start_time);
          const endTime = new Date(testDetails.data.end_time);
          console.log(endTime);
          const currentDate = new Date();
          console.log(currentDate);
          const diffInMilliseconds = currentDate - endTime;

          // if (currentDate < startTime) {
          //   setAttemptMessage("Test has not started yet");
          //   return;
          // } else if (currentDate > endTime) {
          //   setAttemptMessage("Test has Ended");
          //   return;
          // }
          // const openWindows = await axios.get(`http://localhost:8080/window_tracking`);
          //   console.log(openWindows.data);
          //   if(openWindows.data.length > 0){
          //     const filteredWindows = openWindows.data.filter(window =>
          //       window !== 'Program Manager' && window !== 'Windows Input Experience' && window !== 'BMSCE - Proctor - Google Chrome'
          //   );
          //     setWindows(filteredWindows);
          //     setAttemptMessage("Please close all windows before joining a test");
          //     return;
          //   }
          // const response = await axios.get(
          //   "http://localhost:8080/bluetooth/status"
          // );
          // console.log(response.data.bluetooth_on);
          // if (response.data.bluetooth_on) {
          //   setAttemptMessage("Please Off the Bluetooth");
          //   return;
          // }
          // const response2 = await axios.get(
          //   "http://localhost:8080/usb/devices"
          // );
          // console.log(response2.data);
          // if (response2.data.usb_devices.length > 0) {
          //   setAttemptMessage("Please remove USB devices");
          //   return;
          // }

          const addAttempt = await axios.post(
            `http://localhost:5000/api/add-attempt?email=${email}&testCode=${testCode}`
          );
          console.log(addAttempt);
          if (addAttempt.status !== 201) {
            console.log("Error adding attempt");
            return;
          } else {
            if (/Mobi|Android/i.test(navigator.userAgent)) {
              setAttemptMessage("Please Join In Laptop");
              return;
            }
            const durationInMs = endTime - currentDate;
            console.log(durationInMs);
            
            const totalMinutes = Math.floor(durationInMs / (1000 * 60));
            const seconds = Math.floor((durationInMs / 1000) % 60);
            localStorage.setItem("minutes", totalMinutes);
            localStorage.setItem("seconds", seconds);
            localStorage.setItem("testCode", testCode);
            localStorage.setItem("warningCount", 0);
            navigate(`/exam/${testCode}`);
          }
        } else {
          setAttemptMessage("Test Already Attempted");
        }
      }catch (errors){
        console.log(errors)
      }
      } else {
        setAttemptMessage("Please enter a test code.");
      }
    } else {
      console.log("Test code input field not found.");
    }
  };

  const handleClick = async () => {
    const response2 = await axios.get(
      "http://localhost:5000/api/allTests"
    );
    console.log(response2.data);
  }
  
  const handleCreate = () => {
    console.log(localStorage.getItem("role"));
    if (localStorage.getItem("role") === "Student") {
      setMessage("Students aren't allowed to create Test");
    } else {
      navigate("/create");
    }
  };

  return (
    <React.Fragment>
      <div className="section-type landing-page">
        <Navbar />
       
        <div className="landing-content">
          {windows.length > 0 && (
            <ul className="open-windows-list">
              <li>Please Close These windows before Joining the test:</li>
              {windows.map((window, index) => (
                <li key={index}>{window}</li>
              ))}
            </ul>
          )}
          <div className="headings">
            <span className="sub-text">Advanced & Automated</span>
            <span className="main-heading gradient-text">
              Proctoring Solution
            </span>
          </div>

          <p className="desc">
            A straightforward framework built for online proctoring to create
            online tests within minutes, <i>effortlessly</i>.
          </p>
        </div>

        <div className="landing-cta">
          <div onClick={handleCreate}>
            <CtaButton text="Create a test" />
            {message && <p className="errorMessage">{message}</p>}
          </div>

          <p className="desc">OR</p>
          <button onClick={handleClick} className="button"></button>
          <div className="input-item unique-link">
            <div>
              <CommonInput
                placeholderText="Unique test code"
                id="testCode"
                ref={testCodeRef}
              />
              {attemptMessage && (
                <p className="errorMessage">{attemptMessage}</p>
              )}
            </div>
            <span className="join-link">
              <p onClick={handleJoin}>Join</p>
            </span>
          </div>
        </div>

        <div className="features-content">
          <div className="curr-heading">
            <p className="gradient-text">
              <b>Powerful</b> & Lightweight
            </p>
            <h2 className="title-heading">Features</h2>
          </div>

          <div className="all-features">
            {featureList.map((it, index) => (
              <p className="single-feature" key={index}>
                {it}
              </p>
            ))}
          </div>

          {/* <div className="mid-cta">
            <p className="phew">phew...</p>
            <a href="/create">
              <CtaButton />
            </a>
          </div> */}
        </div>

        <div className="final-features">
          <div className="top-sec">
            <div className="left-text">
              <h3 className="gradient-text">Effortlessly integrates with</h3>
              <h1 className="title-heading">
                Google Forms or Microsoft Surveys
              </h1>
            </div>
            <div className="infinite">
              <img src={infinite} alt="infinite" />
              <button onClick={handleClick} className="button"></button>
            </div>

            <div className="right-text">
              <h3 className="gradient-text">The best part?</h3>
              <h1 className="title-heading">Live Status on Admin Dashboard</h1>
            </div>
          </div>

          {/* <div className="mid-cta final-cta">
            <p className="phew">
              And it’s <b>free</b>.
              <br />
              What are you waiting for?
            </p>
            <a href="/create">
              <CtaButton text="Create a test" />
            </a>
          </div> */}
        </div>
      </div>
    </React.Fragment>
  );
};

export default Landing;
