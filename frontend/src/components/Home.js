import React from "react";
import { Typography, Button } from "@material-ui/core";
import BroadcastIcon from "@material-ui/icons/SettingsVoice";
import MessageIcon from "@material-ui/icons/Message";
import AccountIcon from "@material-ui/icons/AccountCircle";
import Cookies from "js-cookie";
import { Redirect } from "react-router";
import TopNavBar from "./TopNavBar";
import Background from "./Background";
import Corgi from "../res/corgi.png";

const Home = (props) => {
  const broadcastHandler = () => {
    props.history.push({
      pathname: `/broadcast`
    });
  };

  const dmHandler = () => {
    props.history.push({
      pathname: `/dm`
    });
  };

  const accountSettingsHandler = () => {
    props.history.push({
      pathname: `/account`
    });
  };

  if (!Cookies.get("username")) {
    return <Redirect to="/login" />;
  }
  return (
    <div>
      <Background />
      <TopNavBar {...props} />
      <div className="flex flex-col mt-40">
        <div className="flex flex-row ml-auto mr-auto">
          <img src={Corgi} width="450" alt="corgi" />
          <div className="p-12 flex items-center justify-center">
            <div className="flex flex-row">
              <div className="flex flex-col">
                <div className="p-12 text-center mt-12 text-4xl">
                  <Typography
                    className="w-full text-6xl text-purple-800"
                    variant="h1"
                  >
                    Boop
                  </Typography>
                </div>
                <div style={{ marginLeft: "150px" }}>
                  <div>
                    <Button onClick={broadcastHandler}>
                      <BroadcastIcon />
                      <div className="ml-4">
                        <Typography className="text-5xl" variant="h4">
                          Broadcast
                        </Typography>
                      </div>
                      <BroadcastIcon className="ml-4" />
                    </Button>
                  </div>
                  <div className="mt-4">
                    <Button onClick={dmHandler}>
                      <MessageIcon />
                      <div className="ml-4">
                        <Typography variant="h4">Private Message</Typography>
                      </div>
                      <MessageIcon className="ml-4" />
                    </Button>
                  </div>
                  <div className="mt-4">
                    <Button onClick={accountSettingsHandler}>
                      <AccountIcon />
                      <div className="ml-4">
                        <Typography variant="h4">Account Details</Typography>
                      </div>
                      <AccountIcon className="ml-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
