import React from 'react';
import { View, StyleSheet } from 'react-native';
import MarketSummary from '../components/MarketSummary';
import CategorySwiper from '../components/CategorySwiper';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <MarketSummary />
      <CategorySwiper />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#161B2E',
    padding: 16,
  },
});
