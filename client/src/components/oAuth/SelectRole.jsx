import React from 'react';
import { useNavigate } from 'react-router-dom';
import './selectRole.css';
import logo from './../../assets/logofont.svg';
import axios from 'axios';

const SelectRole = () => {
  const navigate = useNavigate();

  const handleSelectRole = async (role) => {
    try {
        if(role === "Teacher"){
            const response = await axios.post("http://localhost:5000/api/updateRole",{role,email:localStorage.getItem("email")});
            console.log(response.data);
            localStorage.setItem("role",role);
            navigate('/');
        }
        else{
            navigate('/');
        }
    } catch (error) {
        console.log(error)
    }

  };

  return (
    <div className="role-selection-container">
      <img src={logo} alt="Logo" className="logo" />
      <h1>Select Your Role</h1>
      <div className="role-buttons">
        <button
          className="role-button student-button"
          onClick={() => handleSelectRole('Student')}
        >
          Student
        </button>
        <button
          className="role-button teacher-button"
          onClick={() => handleSelectRole('Teacher')}
        >
          Teacher
        </button>
      </div>
    </div>
  );
};

export default SelectRole;
