import React from 'react';
import { View } from 'react-native';

const Spacer = ({ height = 16, width = 16 }) => {
  return <View style={{ height, width }} />;
};

export default Spacer;
