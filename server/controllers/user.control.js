const User = require("../models/user");

const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");

const register = (req, res) => {
  console.log("Request body:", req.body); // Debugging line
  console.log("Request file:", req.file); // Debugging line

  User.findOne({ email: req.body.formData.email }).exec((error, user) => {
    if (user) return res.json({ msg: "User already registered" });

    const { fullName, email, password, role } = req.body.formData;

    const _user = new User({
      fullName,
      email,
      password,
      role,
    });

    _user.save((error, data) => {
      if (error)
        return res.json({
          msg: "Something happened while storing new user",
          error,
        });
      if (data)
        return res
          .status(201)
          .json({ msg: "New user successfully registered!" });
    });
  });
};

const signIn = (req, res) => {
  User.findOne({ email: req.body.email }) // finding user by email
    .exec((error, user) => {
      // if something happend like internal error
      if (error)
        return res
          .status(400)
          .json({
            msg: "Bad luck!, Must be internal error or you messed up",
            error,
          });
      // if user found then we will verify his password
      if (user) {
        // if password is correct then we will create a token
        if (user.authenticate(req.body.password)) {
          // we will create token
          const token = jwt.sign(
            { id: user._id, email: user.email },
            process.env.jwt_secret_key,
            { expiresIn: "2d" }
          );
          const { _id, fullName, email, profilePicture, role } = user;
          res.cookie("token", token, { expiresIn: "2d" });
          res.status(200).json({
            token,
            user: {
              _id,
              fullName,
              email,
              profilePicture,
              role,
            },
          });
        } else {
          return res.json({ msg: "Invalid password" });
        }
      }
      if (!user) {
        return res.json({ msg: "User does not exist" });
      }
    });
};

const signOut = (req, res) => {
  res.clearCookie("token");
  res.status(200).json({ msg: `Sign-out Successfully...!` });
};

const googleSignIn = async (req, res) => {
  try {
    const user = await User.findOne({ email: req.body.email });
    if (user) {
      const token = jwt.sign(
        { id: user._id, email: user.email },
        process.env.jwt_secret_key,
        { expiresIn: "2d" }
      );
      const { _id, fullName, email, role } = user;
      res.cookie("token", token, { expiresIn: "2d" });
      res.status(200).json({
        token,
        user: {
          _id,
          fullName,
          email,
          role,
        },
      });
    } else {
      const generatedPassword = Math.random().toString(36).slice(-8);
      const hashedPassword = bcrypt.hashSync(generatedPassword, 10);
      const { fullName, email, role } = req.body;

      const _user = new User({
        fullName,
        email,
        password: hashedPassword,
        role,
      });

      _user.save((error, data) => {
        if (error)
          return res.json({
            msg: "Something happened while storing new user",
            error,
          });
        if (data) {
            console.log(data)
          const token = jwt.sign(
            { id: data._id, email: data.email },
            process.env.jwt_secret_key,
            { expiresIn: "2d" }
          );
          const { _id, fullName, email, role } = data;
          res.cookie("token", token, { expiresIn: "2d" });
          res.status(200).json({
            token,
            msg: "New user successfully registered!",
          });
        }
      });
    }
  } catch (error) {
    console.log(error);
  }
};

const getUserDetails = (req, res) => {
  const { email } = req.params;
  User.findOne({ email }).exec((error, user) => {
    if (error)
      return res.status(400).json({ msg: "Something went wrong", error });
    if (user) {
      const { _id, fullName, email, profilePicture } = user;
      return res
        .status(200)
        .json({ user: { _id, fullName, email, profilePicture } });
    } else {
      return res.status(404).json({ msg: "User not found" });
    }
  });
};

const updateRole = async (req, res) => {
  const { email, role } = req.body;

  try {
    const user = await User.findOneAndUpdate(
      { email: email },
      { role: role },
      { new: true }
    );

    if (!user) {
      return res.json({ msg: "User not found" });
    }

    res.status(200).json({ msg: "Role updated successfully", user });
  } catch (error) {
    console.error("Error updating role:", error);
    res.status(500).json({ msg: "Internal server error" });
  }
};

module.exports = {
  register,
  signIn,
  signOut,
  getUserDetails,
  googleSignIn,
  updateRole,
};
