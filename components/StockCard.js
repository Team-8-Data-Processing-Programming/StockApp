import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function StockCard({ stock }) {
  const isUp = stock.change > 0;

  return (
    <View style={styles.card}>
      <Text style={styles.name}>{stock.name}</Text>
      <Text style={styles.price}>{stock.price.toLocaleString()}원</Text>
      <Text style={[styles.rate, { color: isUp ? '#ff5b5b' : '#4a90e2' }]}>
        {isUp ? '+' : ''}
        {stock.change}원 ({stock.rate}%)
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#222',
    padding: 16,
    borderRadius: 12,
    marginBottom: 10,
  },
  name: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  price: {
    color: '#ddd',
    fontSize: 16,
    marginTop: 4,
  },
  rate: {
    marginTop: 4,
    fontSize: 15,
    fontWeight: '500',
  },
});
