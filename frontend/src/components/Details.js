import React, { useState, useEffect } from "react";
import {
  Typography,
  Select,
  MenuItem,
  Button,
  TextField,
  ListItem,
  ListItemText,
  List
} from "@material-ui/core";
import axios from "axios";
import Cookies from "js-cookie";
import Background from "./Background";
import TopNavBar from "./TopNavBar";
import Constants from "../helpers/Constants";

const upiList = "rfro377,aram485,mmir415,baja156,jyao413,skmu104,wyao332,mche226,babe269,jbir297,misl000,bpen264,jxu669,tgre605,jall229,jbea599,jtho434,jchu491,ichu618,admin,tmag741,hwan685,sbud159,dmav894,tzha384,sdup751,ksae900,sbol998,ewon466,kfon596,ahua291,mede607,zyan830,rche647,lken274,jalp521,zlin946,tche562,tche614,utri092,rgos933,tden328,bwil410,akos327,ewar213,jbro682,icam308,lche982,mbre263,rgup198,sdej869,merw957,tant836,crol453,gcoc113,npet532,keva419,zli667,gcao417,jmil565,amon838,mpat750,fsan110,pmal123,lobe655,gwon383,vsta598,ymoh890,jsay091,cryu073,jkim538,qwu536,ntja862,sbha375,rsmi346,vtun547,auma020,ezou149,jall553,mpop344,skim497,ddhy609"
  .split(",")
  .sort();

const Details = (props) => {
  const [block, setBlock] = useState("Select a user to block from here!");
  const [blockList, setBlockList] = useState([]);

  const [friend, setFriend] = useState("Add a friend from here!");
  const [friendList, setFriendList] = useState([]);

  const [word, setWord] = useState("");
  const [wordList, setWordList] = useState([]);

  const onBlockChange = (e) => {
    setBlock(e.target.value);
  };

  const onFriendChange = (e) => {
    setFriend(e.target.value);
  };

  const confirmBlockUser = () => {
    const url = `${Constants.SERVER_URL}/blockUser`;
    axios
      .post(url, {
        username: Cookies.get("username"),
        blockName: block
      })
      .then((res) => {
        console.log(res);
        getBlockUserList();
      })
      .catch((err) => console.log(err));
  };

  const getBlockUserList = () => {
    const url = `${Constants.SERVER_URL}/getBlockedUserList`;
    axios
      .post(url, {
        username: Cookies.get("username")
      })
      .then((res) => {
        console.log(res);
        setBlockList(res.data.split(","));
      })
      .catch((err) => console.log(err));
  };

  useEffect(getBlockUserList, []);

  const blockUserComponent = (
    <div className="flex flex-row">
      <div>
        <Select
          renderValue={(value) => `⚠️   ${value}`}
          autoWidth
          value={block}
          onChange={onBlockChange}
        >
          {upiList.map((x) => (
            <MenuItem value={x}>{x}</MenuItem>
          ))}
        </Select>
      </div>
      <div>
        <Button
          size="small"
          disabled={block === "Select a user to block from here!"}
          onClick={confirmBlockUser}
        >
          Confirm Block
        </Button>
      </div>
    </div>
  );

  const confirmFriend = () => {
    const url = `${Constants.SERVER_URL}/friendUser`;
    axios
      .post(url, {
        username: Cookies.get("username"),
        friendName: friend
      })
      .then((res) => {
        console.log(res);
        getFriendList();
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

  const getFriendList = () => {
    const url = `${Constants.SERVER_URL}/getFriendList`;
    axios
      .post(url, {
        username: Cookies.get("username")
      })
      .then((res) => {
        console.log(res);
        setFriendList(res.data.split(","));
      })
      .catch((err) => console.log(err));
  };

  useEffect(getFriendList, []);

  const editFriendComponent = (
    <div className="flex flex-row">
      <div>
        <Select
          renderValue={(value) => `😊   ${value}`}
          autoWidth
          value={friend}
          onChange={onFriendChange}
        >
          {upiList.map((x) => (
            <MenuItem value={x}>{x}</MenuItem>
          ))}
        </Select>
      </div>
      <div>
        <Button
          onClick={confirmFriend}
          size="small"
          disabled={friend === "Add a friend from here!"}
        >
          Confirm Add!
        </Button>
      </div>
    </div>
  );

  const confirmBlockedWord = () => {
    const url = `${Constants.SERVER_URL}/blockWords`;
    axios
      .post(url, {
        username: Cookies.get("username"),
        blockedWords: word
      })
      .then((res) => {
        console.log(res);
        getBlockedWordList();
      })
      .catch((err) => console.log(err));
  };

  const getBlockedWordList = () => {
    const url = `${Constants.SERVER_URL}/getWordList`;
    axios
      .post(url, {
        username: Cookies.get("username")
      })
      .then((res) => {
        console.log(res);
        setWordList(res.data.split(","));
      })
      .catch((err) => console.log(err));
  };

  useEffect(getBlockedWordList, []);

  const editWordComponent = (
    <div className="flex flex-row">
      <div>
        <TextField
          label="Write a word to block"
          margin="normal"
          onChange={(e) => setWord(e.target.value)}
        />
      </div>
      <div className="mt-8 ml-2">
        <Button
          onClick={confirmBlockedWord}
          disabled={!word.length > 0}
          size="small"
        >
          Confirm Word Block!
        </Button>
      </div>
    </div>
  );

  return (
    <div>
      <Background />
      <TopNavBar {...props} />
      <div className="p-12 mt-6">
        <div className="flex flex-row justify-around mt-12">
          <div>
            <Typography variant="h2"> Edits </Typography>
            <div className="flex flex-col">
              <div className="flex flex-col mt-6">
                <div>
                  <Typography variant="h6"> Edit Blocklist</Typography>
                  {blockUserComponent}
                </div>
              </div>
              <div className="flex flex-col mt-6">
                <Typography variant="h6"> Edit Friendlist</Typography>
                {editFriendComponent}
              </div>
              <div className="flex flex-col mt-6">
                <Typography variant="h6"> Edit Blocked Words</Typography>
                {editWordComponent}
              </div>
            </div>
          </div>
          <div className="">
            <Typography variant="h2"> Lists </Typography>
            <div className="flex flex-col">
              <div className="flex flex-col mt-6">
                <div>
                  <Typography variant="h6"> ⚠️ Blocklist ⚠️</Typography>
                  <List>
                    {blockList.map((el) => {
                      return (
                        <ListItem divider>
                          <ListItemText primary={`🚫${el}`} />
                        </ListItem>
                      );
                    })}
                  </List>
                </div>
              </div>
              <div className="flex flex-col mt-6">
                <div>
                  <Typography variant="h6"> 👨 Friendlist 🙋</Typography>
                  <List>
                    {friendList.map((el) => {
                      return (
                        <ListItem divider>
                          <ListItemText primary={`😃 ${el}`} />
                        </ListItem>
                      );
                    })}
                  </List>
                </div>
              </div>
              <div className="flex flex-col mt-6">
                <div>
                  <Typography variant="h6"> 🤬 Word Block List 🤬</Typography>
                  <List>
                    {wordList.map((el) => {
                      return (
                        <ListItem divider>
                          <ListItemText primary={`🤐 ${el}`} />
                        </ListItem>
                      );
                    })}
                  </List>
                </div>
              </div>
            </div>
          </div>
          <div className="">
            <Typography variant="h2"> Favourites </Typography>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Details;
