import React, { useState, useEffect } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import logo from "./../../assets/logofont.svg";
import { CommonInput, CopyLink, CtaButton, Navbar } from "../../components";
import "./editTest.css";

const inputField = [  
  { label: "Test Name", name: "testName" },
  { label: "Test Form Link", name: "testLink" },
  { label: "mm/dd/yy - hh:mm", name: "startTime" },
  { label: "Duration", name: "duration" },
  { label: "Total Candidates", name: "totalCandidates" },
  { label: "Keywords", name: "keywords" },
];

const EditTest = () => {
  const email = localStorage.getItem("email");
  const location = useLocation();
  const { testCode } = location.state;
  const [message, setMessage] = useState("");
  const [formData, setFormData] = useState({
    email: email,    
    testName: "",
    testLink: "",
    startTime: "",
    duration: "",
    totalCandidates: "",
    keywords: "",
  });
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem("token");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  useEffect(() => {
    // Fetch test details using testCode
    const fetchTestDetails = async () => {
      try {        
        const response = await axios.get(`http://localhost:5000/api/test-details/${testCode}`);
        const testDetails = response.data;
        const startTimeIST = new Date(testDetails.start_time).toLocaleString("en-IN", {
            timeZone: "Asia/Kolkata",
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
          });
  
          // Calculate duration in minutes
          const startTime = new Date(testDetails.start_time);
          const endTime = new Date(testDetails.end_time);
          const duration = (endTime - startTime) / (1000 * 60); // duration in minutes
  
          // Convert keywords array to space-separated string
          console.log(testDetails.keywords,testDetails)
          const keywords = testDetails.keywords.join(" ");
          console.log(keywords)
  
        setFormData({
          email: email,          
          testName: testDetails.test_name,
          testLink: testDetails.test_link_by_user,
          startTime: startTimeIST,
          duration: duration,
          totalCandidates: testDetails.no_of_candidates_appear,
          keywords: keywords,
        });
      } catch (error) {
        console.error("There was an error fetching the test details!", error);
      }
    };

    fetchTestDetails();
  }, [testCode, email]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const emptyFields = Object.keys(formData).filter((key) => !formData[key]);
      console.log(emptyFields);
      if (emptyFields.length !== 0) {
        setMessage("Enter all the fields");
        return;
      }
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://localhost:5000/api/update-test",
        {formData,testCode }       
      );
      setMessage(response.data.msg);
      console.log("Response from server:", response.data);
      if (response.status === 201) {
        console.log(response.data);      
        navigate("/dashboard"); 
      }
    } catch (error) {
      console.error("There was an error creating the test!", error);
      setMessage("There was an error creating the test!")
    }
  };

  

  return (
    <div className="client-create">
      <Navbar />

      <div className="create-form">
        <h1 className="title-heading">EDIT</h1>
        <form onSubmit={handleSubmit}>
          <div className="input-fields">
            {inputField.map((item, index) => (
              <div key={index}>
                <CommonInput
                  key={index}
                  placeholderText={item.label}
                  name={item.name}
                  value={formData[item.name]}
                  onChange={handleInputChange}
                  type={"text"}
                />
              </div>
            ))}
          </div>
          {message && <p className="errorMessage">{message}</p>}
          <CtaButton text="Edit Test" />
        </form>
      </div>
    </div>
  );
};

export default EditTest;
