import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { ApolloProvider } from 'react-apollo';
import client from './apollo';
import { GitHubStars } from './GitHubStars';
import { GitHubStarsPerDay } from './GitHubStarsPerDay';

class App extends Component {
  render() {
    return (
      <ApolloProvider client={client}>
        <div className="App">
          <header className="App-header displayFlex">
            <div className="container displayFlex">
              <img src={logo} className="App-logo" alt="logo" />
              <h1 className="App-title">Hasura Stats</h1>
            </div>
          </header>

          <GitHubStars />
          <GitHubStarsPerDay />

        </div>
      </ApolloProvider>
    );
  }
}

export default App;
