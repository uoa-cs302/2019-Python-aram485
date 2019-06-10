import React, { useState, useEffect, useCallback } from "react";
import {
  TextField,
  ListItem,
  List,
  ListItemText,
  Divider,
  Button,
  Typography,
  MenuItem
} from "@material-ui/core";
import axios from "axios";
import Cookies from "js-cookie";
import moment from "moment";
import _ from "lodash";
import FilterList from "@material-ui/icons/FilterList";
import Select from "@material-ui/core/Select";
import Background from "./Background";
import TopNavBar from "./TopNavBar";
import Constants from "../helpers/Constants";

const upiList = "rfro377,aram485,mmir415,baja156,jyao413,skmu104,wyao332,mche226,babe269,jbir297,misl000,bpen264,jxu669,tgre605,jall229,jbea599,jtho434,jchu491,ichu618,admin,tmag741,hwan685,sbud159,dmav894,tzha384,sdup751,ksae900,sbol998,ewon466,kfon596,ahua291,mede607,zyan830,rche647,lken274,jalp521,zlin946,tche562,tche614,utri092,rgos933,tden328,bwil410,akos327,ewar213,jbro682,icam308,lche982,mbre263,rgup198,sdej869,merw957,tant836,crol453,gcoc113,npet532,keva419,zli667,gcao417,jmil565,amon838,mpat750,fsan110,pmal123,lobe655,gwon383,vsta598,ymoh890,jsay091,cryu073,jkim538,qwu536,ntja862,sbha375,rsmi346,vtun547,auma020,ezou149,jall553,mpop344,skim497,ddhy609"
  .split(",")
  .sort()
  .map((upi) => <MenuItem value={upi}>{upi}</MenuItem>);

const Broadcast = (props) => {
  const [message, setMessage] = useState("");
  const [broadcastList, setBroadcastList] = useState([]);
  const [upi, setUpi] = useState("Everyone");
  const [filterUpiList, setFilterUpiList] = useState([]);
  const [filterMessage, setFilterMessage] = useState("");
  const [filterMessageList, setFilterMessageList] = useState([]);

  const validMessage = message.length > 0;

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

  const confirmBroadcast = () => {
    const broadcastUrl = `${Constants.SERVER_URL}/tx_broadcast`;
    axios
      .post(broadcastUrl, {
        username: Cookies.get("username"),
        message
      })
      .then((res) => console.log(res))
      .catch((err) => console.log(err));
  };

  const pollBroadcast = () => {
    const getBroadcastUrl = `${Constants.SERVER_URL}/get_broadcast`;
    axios
      .get(getBroadcastUrl)
      .then((res) => {
        console.log(res);
        const { data } = res;
        data.sort((a, b) => b[0] - a[0]);
        data.forEach((msg) => {
          const unixTime = msg[0];
          const normalTime = moment.unix(unixTime).format("DD-MM-YY HH:mm:ss");
          msg[0] = normalTime;
        });

        if (!_.isEqual(data, broadcastList)) {
          setBroadcastList(data);
        }
      })
      .catch((err) => console.log(err));
  };

  const listMap = broadcastList.map((el) => {
    const username = el[1];
    const msg = el[2];
    const date = el[0];
    const secondaryMessage = `From ${username} At ${date}`;
    return (
      <ListItem divider>
        <ListItemText
          className="break-words w-20"
          primary={msg}
          secondary={secondaryMessage}
        />
      </ListItem>
    );
  });

  useEffect(() => {
    pollBroadcast();
    setInterval(pollBroadcast, 5000);
  }, []);

  const onSelectChange = (e) => {
    setUpi(e.target.value);
    const filterSenderURL = `${Constants.SERVER_URL}/filter_by_sender`;
    axios
      .post(filterSenderURL, {
        username: e.target.value
      })
      .then((res) => {
        console.log(res);
        setFilterUpiList(res.data);
      })
      .catch((err) => console.log(err));
  };

  const onFilterWordChange = (e) => {
    setFilterMessage(e.target.value);
    const filterSenderWord = `${Constants.SERVER_URL}/filter_by_word`;
    axios
      .post(filterSenderWord, {
        word: e.target.value
      })
      .then((res) => {
        console.log(res);
        setFilterMessageList(res.data);
      })
      .catch((err) => console.log(err));
  };

  return (
    <div>
      <Background />
      <TopNavBar {...props} />
      <div className="p-12 flex items-center justify-center mt-6">
        <div className="flex flex-row">
          <div className="flex flex-col m">
            <div className="flex flex-row">
              <TextField
                label="Broadcast a message"
                margin="normal"
                onChange={(e) => setMessage(e.target.value)}
              />
              <div className="mt-8 ml-4">
                <Button onClick={confirmBroadcast} disabled={!validMessage}>
                  Confirm
                </Button>
              </div>
            </div>
            <div className="flex flex-col mt-4">
              <List>{listMap}</List>
            </div>
          </div>
          <div className="ml-24 mt-6">
            <div className="flex flex-row">
              <div>
                <Typography variant="h4" className="text-center">
                  Filters
                </Typography>
              </div>
              <div className="ml-2 mt-2">
                <FilterList />
              </div>
            </div>

            <div className="flex flex-col">
              <div className="flex flex-col">
                <div className="flex flex-row mt-6">
                  <Typography> List Broadcasts from </Typography>
                  <div className="ml-2" style={{ marginTop: "-3px" }}>
                    <Select autoWidth value={upi} onChange={onSelectChange}>
                      {upiList}
                    </Select>
                  </div>
                </div>
              </div>

              <div className="flex flex-col">
                <List>
                  {filterUpiList.map((el) => {
                    return (
                      <ListItem divider>
                        <ListItemText primary={el[1]} secondary={el[0]} />
                      </ListItem>
                    );
                  })}
                </List>
              </div>
              <div className="flex flex-row mt-6">
                <div className="flex flex-row">
                  <div>
                    <Typography> List Broadcasts with word: </Typography>
                  </div>
                  <div className="ml-2" style={{ marginTop: "-37px" }}>
                    <TextField
                      onChange={onFilterWordChange}
                      label="Type in a word"
                      margin="normal"
                    />
                  </div>
                </div>
              </div>
              <div className="flex flex-col">
                <List>
                  {filterMessage.length > 0 &&
                    filterMessageList.map((el) => {
                      console.log(el);
                      return (
                        <ListItem divider>
                          <ListItemText primary={el[1]} secondary={el[0]} />
                        </ListItem>
                      );
                    })}
                </List>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Broadcast;
