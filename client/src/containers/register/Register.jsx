import React, { useState } from "react";
import axios from "axios";
import logo from "./../../assets/logofont.svg";
import human from "./../../assets/human.svg";
import { CommonInput, CtaButton, WebcamCapture } from "../../components";
import "./register.css";
import { useNavigate } from "react-router";
import OAuth from "../../components/oAuth/OAuth";

const inputField = [
  { name: "email", type: "text" },
  { name: "fullName", type: "text" },
  { name: "password", type: "password" },
  { name: "role", type: "select", options: ["Student", "Teacher"] },
];

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    fullName: "",
    password: "",
    role: "",
  });
  const [message, setMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const validateEmail = async (email) => {
    const response = await axios.get(
      `https://emailvalidation.abstractapi.com/v1/?api_key=69ef4bc76e3e41988bef4d2c1ab81b7d&email=${email}`
    );
    console.log(response.data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const emptyFields = Object.keys(formData).filter((key) => !formData[key]);
    console.log(emptyFields);
    if (emptyFields.length !== 0) {
      setMessage("Enter all the fields");
      return;
    }
    // validateEmail(formData.email);
    const form = new FormData();
    form.append("email", formData.email);
    form.append("fullName", formData.fullName);
    form.append("password", formData.password);
    form.append("role", formData.role);
    // if (formData.profilePicture) {
    //     form.append('profilePicture', formData.profilePicture);
    // }

    console.log("Form data before submission:", formData); // Debugging line

    try {
      const response = await axios.post("http://localhost:5000/api/register", {
        formData,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("Response from server:", response.data); // Debugging line
      if (response.status === 201) {
        setSuccessMessage("New User Registered Successfully");
        setFormData({
          email: "",
          fullName: "",
          password: "",
          role: "",
        });
        setTimeout(() => {
          navigate("/login");
        }, 1000);
      } else {
        setMessage(response.data.msg);
      }
    } catch (error) {
      console.error("There was an error registering!", error);
    }
  };

  return (
    <div className="user-register">
      <div className="logo">
        <img src={logo} alt="aankh-logo" />
      </div>
      <div className="register-form">
        <h1 className="title-heading">Register</h1>
        <form onSubmit={handleSubmit}>
          <div className="input-fields">
            {inputField.map((item, index) => (
              <div key={index}>
                {item.type === "select" ? (
                  <div>
                    <span className="label">Role:</span>
                    <select
                      name={item.name}
                      value={formData[item.name]}
                      onChange={handleInputChange}
                      className="select"
                    >
                      <option value="" disabled>
                        Select {item.name}
                      </option>
                      {item.options.map((option, idx) => (
                        <option key={idx} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : (
                  <CommonInput
                    placeholderText={item.name}
                    name={item.name}
                    value={formData[item.name]}
                    onChange={handleInputChange}
                    type={item.type}
                  />
                )}
              </div>
            ))}
          </div>
          {/* <div className="image-capture">
                        <img src={human} alt="human-outline" />
                        <WebcamCapture setImage={(img) => setFormData({ ...formData, profilePicture: img })} />
                    </div> */}
          {message && <div className="errorMessage">{message}</div>}
          
          <CtaButton text="Register" />
          <OAuth />

        </form>
        {successMessage && (
          <div className="success-message">{successMessage}</div>
        )}
      </div>
    </div>
  );
};

export default Register;
