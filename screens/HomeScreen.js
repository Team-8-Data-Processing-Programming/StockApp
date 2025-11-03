import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import StockCard from '../components/StockCard';

export default function HomeScreen() {
  const stockData = [
    { id: '1', name: '삼성전자', price: 71800, change: 1200, rate: 1.7 },
    { id: '2', name: 'SK하이닉스', price: 134500, change: -2500, rate: -1.82 },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📈 코스피 2,547.78 (+0.49%)</Text>
      <FlatList
        data={stockData}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <StockCard stock={item} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111',
    padding: 16,
  },
  title: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 12,
  },
});
