import React, { useEffect, useState } from "react";
import logo from "./../../assets/logofont.svg";
import { CopyLink, Terminated, PieChart, Navbar } from "../../components";
import "./status.css";
import axios from "axios";
import { useLocation } from "react-router";

const mockList = [
  {
    studentID: "1902112",
    warningCnt: 5,
    message: "DevTools detected",
  },
  {
    studentID: "1902141",
    warningCnt: 4,
    message: "Noise detected",
  },
  {
    studentID: "1902114",
    warningCnt: 6,
    message: "Face covered",
  },
  {
    studentID: "1902154",
    warningCnt: 2,
    message: "Full Screen Closed",
  },
];

const Status = () => {
  const [warnings, setWarnings] = useState([]);
  const location = useLocation();
  const { testCode, name, time } = location.state || {};
  console.log(testCode, name, time);
  const getWarnings = () => {
    const role = localStorage.getItem("role"); // Assuming role is stored in localStorage

    if (role === "Teacher") {
      axios
        .get(`http://localhost:5000/api/get-all-warnings?testCode=${testCode}`)
        .then((response) => {
          const warnings = response.data.warnings;
          console.log(warnings);
          setWarnings(warnings);
        })
        .catch((error) => {
          console.error("Error fetching warnings for all students:", error);
        });
    } else {
      const email = localStorage.getItem("email");
      axios
        .get(
          `http://localhost:5000/api/get-warning?email=${email}&testCode=${testCode}`
        )
        .then((response) => {
          console.log(response);
          const warnings = response.data.warnings;
          console.log(warnings);
          setWarnings(warnings);
        })
        .catch((error) => {
          console.error("Error fetching warnings:", error);
        });
    }
  };

  useEffect(() => {
    getWarnings();
  }, []);
  return (
    <div className="status-dashboard">
      <Navbar />
      <h1 className="title-heading">Test Dashboard</h1>

      <div className="test-details">
        <div className="test-item">
          <h4 className="test-time">{time}</h4>

          <h4 className="test-name">{name}</h4>

          {/* <CopyLink link={testCode} /> */}
        </div>
      </div>
      {/* <div className="charts">
        <PieChart />
      </div> */}
      <div className="terminated-students">
        <h2 className="title-heading">Warnings</h2>
        
          {localStorage.getItem("role") === "Student" ? (
            <div className="terminated-boxes">
              {warnings.length > 0 &&
                warnings.map((item) => (
                  <Terminated item={item} key={item.studentID} />
                ))}
            </div>
          ) : (
            <div className="terminated-boxes">
              {warnings.length > 0 &&
                warnings.map((student, index) => (
                  <div key={index} className="student-box">
                    <h3>{student.email}</h3>
                    {student.warnings.map((warning, warningIndex) => (
                      <div>
                        {warning.warningType}:{warning.warningCount}
                      </div>
                    ))}
                  </div>
                ))}
            </div>
          )}
        

        {warnings.length === 0 && <p className="no-warnings">No Warnings</p>}
      </div>
    </div>
  );
};

export default Status;
