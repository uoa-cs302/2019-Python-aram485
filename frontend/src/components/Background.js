import React from 'react';
import { Helmet } from 'react-helmet';

const Background = () => {
  return (
    <Helmet>
      <style>{'body { background-color: #fdfd96; }'}</style>
    </Helmet>
  );
};

export default Background;
