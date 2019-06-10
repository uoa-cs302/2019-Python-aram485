import React from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import Home from "./components/Home";
import Login from "./components/Login";
import Broadcast from "./components/Broadcast";
import Dm from "./components/Dm";
import Details from "./components/Details";

function App() {
  return (
    <div>
      <Router>
        <Switch>
          <Route exact path="/" render={(props) => <Home {...props} />} />
          <Route
            path="/broadcast"
            render={(props) => <Broadcast {...props} />}
          />
          <Route path="/dm" render={(props) => <Dm {...props} />} />
          <Route path="/account" render={(props) => <Details {...props} />} />
          <Route path="/login" render={(props) => <Login {...props} />} />
        </Switch>
      </Router>
    </div>
  );
}

export default App;
