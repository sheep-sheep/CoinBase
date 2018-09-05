import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import Dashboard from './App';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(<Dashboard />, document.getElementById('root'));
registerServiceWorker();
