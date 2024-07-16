import React from "react";
import {GoogleAuthProvider, getAuth, signInWithPopup} from 'firebase/auth';
import { app } from "../../firebase";
import { useNavigate } from "react-router-dom";
import CtaButton from "../ctabutton/CtaButton.jsx";
import axios from "axios";
import './oAuth.css'

export default function OAuth() {  
  const navigate = useNavigate();
  const handleGoogleCLick = async () =>{
    try {
      const provider = new GoogleAuthProvider();
      const auth = getAuth(app);

      const result = await signInWithPopup(auth,provider);

      console.log(result);

      const response = await axios.post(
        "http://localhost:5000/api/googleSignIn",
        {fullName:result.user.displayName,email:result.user.email,role:"Student"}
      );
      console.log("Response from server:", response.data);
      localStorage.setItem("email", result.user.email);
      localStorage.setItem("fullName", result.user.displayName);
      
      
      if(response.data.user){
        localStorage.setItem("role", response.data.user.role);
        localStorage.setItem("token",response.data.token)
        navigate("/");
      }else{
        localStorage.setItem("token",response.data.token)
        localStorage.setItem("role","Student")
        navigate('/selectRole')
      }    
    } catch (error) {
      console.log(error)
    }
  }
  return (
    <div onClick={handleGoogleCLick}>
        <button type="button" className="oAuth">Continue with Google</button>
    </div>
  ); 
}
