import React, { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  MenuItem,
  Select
} from "@material-ui/core";
import Cookies from "js-cookie";
import Axios from "axios";
import Constants from "../helpers/Constants";

const useStyles = makeStyles((theme) => ({
  menuButton: {
    marginRight: theme.spacing(2)
  },
  title: {
    flexGrow: 2
  },
  appBar: {
    backgroundColor: "#514095"
  },
  boopText: {
    width: "100%",
    maxWidth: 500
  }
}));

const TopNavBar = (props) => {
  const [status, setStattus] = useState(Cookies.get("status"));

  const classes = useStyles();
  const welcomeText = `Welcome ${Cookies.get("username")}`;
  const logoutHandler = () => {
    const url = `${Constants.SERVER_URL}/push_data`;
    Axios.get(url)
      .then((res) => console.log(res))
      .catch((err) => console.log(err));
    Cookies.remove("username");
    props.history.push("/login");
  };

  const homeHandler = () => {
    props.history.push("/");
  };

  const broadcastHandler = () => {
    props.history.push("/broadcast");
  };

  const dmHandler = () => {
    props.history.push("/dm");
  };

  const accountHandler = () => {
    props.history.push("/account");
  };

  const onSelectChange = (e) => {
    let endpoint;

    setStattus(e.target.value);

    const tempStatus = e.target.value;

    if (tempStatus === "Online") {
      endpoint = "amOnline";
    }

    if (tempStatus === "Busy") {
      endpoint = "amBusy";
    }

    if (tempStatus === "Away") {
      endpoint = "amAway";
    }

    if (tempStatus === "Offline") {
      endpoint = "amOffline";
    }

    const url = `${Constants.SERVER_URL}/${endpoint}`;

    Axios.get(url)
      .then((res) => console.log(res))
      .catch((err) => console.log(err));

    Cookies.set("status", tempStatus);
  };

  return (
    <div>
      <AppBar className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6" className="flex-grow">
            {welcomeText}
          </Typography>
          <div className="flex flex-row">
            <Select value={status} onChange={onSelectChange}>
              <MenuItem value="Online">Online</MenuItem>
              <MenuItem value="Busy"> Busy </MenuItem>
              <MenuItem value="Away"> Away </MenuItem>
              <MenuItem value="Offline"> Offline </MenuItem>
            </Select>
            <Button onClick={homeHandler} color="inherit">
              Home
            </Button>
            <Button onClick={broadcastHandler} color="inherit">
              Broadcast
            </Button>
            <Button onClick={dmHandler} color="inherit">
              Private Message
            </Button>
            <Button onClick={accountHandler} color="inherit">
              Account
            </Button>
            <Button onClick={logoutHandler} color="inherit">
              Logout
            </Button>
          </div>
        </Toolbar>
      </AppBar>
    </div>
  );
};

export default TopNavBar;
