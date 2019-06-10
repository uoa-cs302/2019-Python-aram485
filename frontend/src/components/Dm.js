import React, { useState, useEffect } from "react";
import {
  Typography,
  TextField,
  Select,
  Button,
  MenuItem,
  CircularProgress,
  List,
  ListItem,
  ListItemText
} from "@material-ui/core";
import axios from "axios";
import Cookies from "js-cookie";
import Background from "./Background";
import TopNavBar from "./TopNavBar";
import Constants from "../helpers/Constants";

const upiList = "rfro377,aram485,mmir415,baja156,jyao413,skmu104,wyao332,mche226,babe269,jbir297,misl000,bpen264,jxu669,tgre605,jall229,jbea599,jtho434,jchu491,ichu618,admin,tmag741,hwan685,sbud159,dmav894,tzha384,sdup751,ksae900,sbol998,ewon466,kfon596,ahua291,mede607,zyan830,rche647,lken274,jalp521,zlin946,tche562,tche614,utri092,rgos933,tden328,bwil410,akos327,ewar213,jbro682,icam308,lche982,mbre263,rgup198,sdej869,merw957,tant836,crol453,gcoc113,npet532,keva419,zli667,gcao417,jmil565,amon838,mpat750,fsan110,pmal123,lobe655,gwon383,vsta598,ymoh890,jsay091,cryu073,jkim538,qwu536,ntja862,sbha375,rsmi346,vtun547,auma020,ezou149,jall553,mpop344,skim497,ddhy609"
  .split(",")
  .sort();

const Dm = (props) => {
  const [sendTo, setSendTo] = useState("");
  const [message, setMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [userList, setUserList] = useState([]);
  const [messageList, sentMessageList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilterList] = useState([]);
  let count = 0;

  const getUserList = () => {
    const url = `${Constants.SERVER_URL}/currentlyOnline`;
    if (count === 0) {
      setLoading(true);
      count += 1;
    }
    axios
      .post(url, {
        username: Cookies.get("username")
      })
      .then((res) => {
        console.log(res);
        setLoading(false);
        setUserList(res.data.sort());
      })
      .catch((err) => console.log(err));
  };

  const getMessageList = () => {
    const url = `${Constants.SERVER_URL}/getRecentDMs`;
    axios
      .post(url, {
        username: Cookies.get("username")
      })
      .then((res) => {
        console.log(res);
        sentMessageList(res.data);
      })
      .catch((err) => console.log(err));
  };

  const report = () => {
    const clientUrl = `${Constants.SERVER_URL}/client_report`;
    axios
      .post(clientUrl, {
        username: Cookies.get("username")
      })
      .then((res) => console.log(res))
      .catch((err) => console.log(err));
  };

  useEffect(() => {
    setInterval(report, 250000);
  }, []);

  const onSendClick = () => {
    const url = `${Constants.SERVER_URL}/tx_privateMessage`;
    axios
      .post(url, {
        username: Cookies.get("username"),
        sendToUsername: sendTo,
        message
      })
      .then((res) => console.log(res))
      .catch((err) => console.log(err));
  };

  const filterChange = (e) => {
    setSearchQuery(e.target.value);
    const url = `${Constants.SERVER_URL}/filter_by_senderPM`;
    axios
      .post(url, {
        username: e.target.value
      })
      .then((res) => {
        console.log(res);
        setFilterList(res.data);
      })
      .catch((err) => console.log(err));
  };

  useEffect(() => {
    getUserList();
    setInterval(getUserList, 60000);
  }, []);

  useEffect(() => {
    getMessageList();
    setInterval(getMessageList, 10000);
  }, []);

  return (
    <div>
      <Background />
      <TopNavBar {...props} />
      <div className="p-12 mt-6">
        <div className="flex flex-row justify-around mt-12">
          <div className="flex flex-col">
            <div>
              <Typography variant="h4"> Send a DM 😏!</Typography>
              <div className="flex flex-col mt-4">
                <div className="flex flex-row">
                  <Typography variant="h6">
                    Person you want to send to:
                  </Typography>
                  <div className="ml-1">
                    <div className="ml-2">
                      {loading && <CircularProgress color="primary" />}
                    </div>
                    {!loading && (
                      <Select
                        onChange={(e) => setSendTo(e.target.value)}
                        autowidth
                        value={sendTo}
                      >
                        {userList.map((x) => (
                          <MenuItem value={x}>{x}</MenuItem>
                        ))}
                      </Select>
                    )}
                  </div>
                </div>
                <div className="flex flex-row mt-3">
                  <Typography variant="h6">
                    Message you want to send:
                  </Typography>
                  <div className="ml-1">
                    <TextField onChange={(e) => setMessage(e.target.value)} />
                  </div>
                </div>
                <div className="mt-2">
                  <Button
                    fullWidth
                    variant="contained"
                    className="bg-blue-200"
                    color="primary"
                    size="small"
                    onClick={onSendClick}
                    disabled={!(sendTo.length > 0 && message.length > 0)}
                  >
                    <Typography>Send! ✈️ </Typography>
                  </Button>
                </div>
              </div>
            </div>
            <div className="mt-12">
              <Typography variant="h4"> Search your DM's 😜!</Typography>
              <div className="flex flex-col mt-4">
                <div className="flex flex-row">
                  <div>
                    <Typography variant="h6">Search by</Typography>
                  </div>
                  <div className="ml-2">
                    <Select
                      onChange={filterChange}
                      autowidth
                      value={searchQuery}
                    >
                      {upiList.map((x) => (
                        <MenuItem value={x}>{x}</MenuItem>
                      ))}
                    </Select>
                  </div>
                </div>
                <div className="flex flex-col">
                  <Typography variant="h6">Results:</Typography>
                  <div className="flex flex-col">
                    <List>
                      {filter.length === 0 && searchQuery.length > 0 && (
                        <Typography>
                          Sorry this person has not DM'd you
                        </Typography>
                      )}
                      {filter.length > 0 &&
                        filter.map((x) => {
                          return (
                            <ListItem divider>
                              <ListItemText primary={x[1]} secondary={x[0]} />
                            </ListItem>
                          );
                        })}
                    </List>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div>
            <Typography variant="h2"> Most recent DM's 🤤!</Typography>
            <div className="flex flex-col">
              <List>
                {messageList.map((x) => {
                  return (
                    <ListItem divider>
                      <ListItemText primary={x[1]} secondary={x[0]} />
                    </ListItem>
                  );
                })}
              </List>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dm;
