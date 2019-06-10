import React, { useState } from "react";
import { Typography, TextField, Button, Snackbar } from "@material-ui/core";
import ArrowForwardIcon from "@material-ui/icons/ArrowForward";
import axios from "axios";
import CircularProgress from "@material-ui/core/CircularProgress";
import { Redirect } from "react-router";
import Cookies from "js-cookie";
import Background from "./Background";
import Constants from "../helpers/Constants";

const Login = (props) => {
  const [username, setUsername] = useState("");
  const [specialKey, setSpecialKey] = useState("");
  const [password, setPassword] = useState(""); // all variables have an attached setter
  const [loading, setLoading] = useState(false);
  const [onErr, setOnErr] = useState(false);
  const valid = username.length > 0 && password.length > 0;

  const onLoginClick = () => {
    setLoading(true);

    const loginUrl = `${Constants.SERVER_URL}/signin`;
    axios
      .post(loginUrl, {
        username,
        password,
        specialKey
      })
      .then((res) => {
        setLoading(false);
        Cookies.set("username", username);
        Cookies.set("specialKey", specialKey);
        props.history.push({
          pathname: `/`
        });
      })
      .catch((err) => {
        console.log(err.response);
        setLoading(false);
        setOnErr(true);
        setTimeout(() => setOnErr(false), 2000);
      });
  };

  if (Cookies.get("username")) {
    return <Redirect to="/" />;
  }

  return (
    <div>
      <Snackbar
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
        key="top,right"
        open={onErr}
        ContentProps={{
          "aria-describedby": "message-id"
        }}
        message={<span id="message-id">Incorrect Username or Password</span>}
      />
      <Background />
      <div className="p-12 flex items-center justify-center mt-64">
        <div className="flex flex-col">
          <div className="text-center">
            <Typography
              className="w-full text-6xl text-purple-800"
              variant="h1"
            >
              Login
            </Typography>
          </div>
          <div className="flex flex-col mt-8">
            <TextField
              label="Username"
              margin="normal"
              onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
              type="password"
              label="Password"
              margin="normal"
              onChange={(e) => setPassword(e.target.value)}
            />
            <TextField
              type="password"
              label="Special key"
              margin="normal"
              onChange={(e) => setSpecialKey(e.target.value)}
            />
            <div className="mt-6">
              <Button
                onClick={onLoginClick}
                disabled={!valid}
                variant="contained"
                className=""
                color="primary"
                fullWidth
              >
                {loading && <CircularProgress color="secondary" />}
                {!loading && <ArrowForwardIcon />}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
