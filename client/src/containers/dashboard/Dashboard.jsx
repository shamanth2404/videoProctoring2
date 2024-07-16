import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "./../../assets/logofont.svg";
import { CopyLink, Navbar } from "../../components";
import "./dashboard.css";
import axios from "axios";

const Dashboard = () => {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const isAuthenticated = !!localStorage.getItem("token");
  const email = localStorage.getItem("email");
  const role = localStorage.getItem("role");
  useEffect(() => {
    const fetchTests = async () => {
      try {
        let createdTests;
        if (role === "Teacher") {
          createdTests = await axios.get(
            `http://localhost:5000/api/createdTests?email=${email}`
          );
          setTests(createdTests.data);
        } else {
          createdTests = await axios.get(
            `http://localhost:5000/api/getAttempts?email=${email}`
          );
          console.log(createdTests.data[0]);
          const testCodes = createdTests.data[0].tests.map(
            (test) => test.testCode
          );
          console.log(testCodes);
          const matchedTests = await axios.post(
            "http://localhost:5000/api/getAttemptedTestNames",
            { testCodes }
          );
          const attempts = createdTests.data[0].tests;
          const testNames = matchedTests.data;
          console.log(testNames);
          // Create a map for quick lookup of test names by testcode
          const testNameMap = {};
          testNames.forEach((test) => {
            testNameMap[test.test_code] = test.test_name;
          });

          // Merge attempts and test names
          const mergedData = attempts.map((attempt) => ({
            testcode: attempt.testCode,
            attemptedTime: attempt.createdAt,
            testname: testNameMap[attempt.testCode], // Lookup the test name using the testcode
          }));

          // Set the merged data in state
          setTests(mergedData);
        }

        console.log(tests);
      } catch (error) {
        console.error("Error fetching tests:", error);
      }
    };

    fetchTests();
  }, []);

  useEffect(() => {
    console.log(tests);
  }, [tests]);

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    const options = { timeZone: "Asia/Kolkata", hour12: true };
    const dateStr = date.toLocaleDateString("en-GB", options); // Format as dd/mm/yyyy
    const timeStr = date.toLocaleTimeString("en-GB", options); // Format as hh:mm:ss AM/PM
    return `${dateStr}, ${timeStr}`;
  };

  // useEffect(() => {
  //     if (!isAuthenticated) {
  //         navigate('/login');
  //     }
  // }, [isAuthenticated, navigate]);

  return (
    <div className="section-type admin-dashboard">
      <Navbar />

      <h1 className="title-heading"> Dashboard</h1>
      <div className="user-info">
        <p>
          <strong>Name:</strong> {localStorage.getItem("fullName")}
        </p>
        <p>
          <strong>Email:</strong> {localStorage.getItem("email")}
        </p>
        <p>
          <strong>Role:</strong> {localStorage.getItem("role")}
        </p>
      </div>
      <div className="test-dashboard">
        <h2 className="title-heading">Tests</h2>

        <div className="test-items">
          {tests.length !== 0 ? (
            tests.map((test) => (
              <Link
                to="/status"
                state={{
                  testCode: test.testcode || test.test_code,
                  name: test.testname || test.test_name,
                  time: test.start_time
                    ? formatDateTime(test.start_time)
                    : formatDateTime(test.attemptedTime),
                }}
                key={test.testcode || test.test_code}
              >
                {role === "Teacher" ? (
                  <div className="test-item" key={test.test_code}>
                    <h4 className="test-time">
                      {formatDateTime(test.start_time)}
                    </h4>
                    <h4 className="test-name">
                      <a href="/status">{test.test_name}</a>
                    </h4>
                    <CopyLink link={test.test_code} />
                    <Link
                      to="/editTest"
                      state={{
                        testCode: test.test_code,                        
                      }}
                      key={test.test_code}
                    >
                      {" "}
                      <button className="editButton">EDIT</button>
                    </Link>
                  </div>
                ) : (
                  <div className="test-item" key={test.testcode}>
                    <h4 className="test-name">
                      <a href="/status">{test.testname}</a>
                    </h4>
                    <h4 className="test-time">
                      {formatDateTime(test.attemptedTime)}
                    </h4>
                    <button className="editButton">See Details</button>
                  </div>
                )}
              </Link>
            ))
          ) : (
            <p>No Tests {role === "Teacher" ? "Created" : "Attempted "}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
