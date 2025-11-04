import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function MarketSummary() {
  const marketData = [
    { id: '1', name: 'KOSPI', value: 2567.89, change: 0.6 },
    { id: '2', name: 'KOSDAQ', value: 745.32, change: -0.46 },
    { id: '3', name: 'NASDAQ', value: 14823.43, change: 0.85 },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.title}>시장 현황 📊</Text>
      <View style={styles.row}>
        {marketData.map((item) => {
          const isUp = item.change > 0;
          return (
            <View key={item.id} style={styles.card}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.value}>{item.value.toLocaleString()}</Text>
              <Text
                style={[styles.change, { color: isUp ? '#4CAF50' : '#FF5B5B' }]}
              >
                {isUp ? '↗ +' : '↘ '}
                {item.change.toFixed(2)}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1E2336',
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  title: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 10,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  card: {
    flex: 1,
    backgroundColor: '#161B2E',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  name: {
    color: '#B0B3C2',
    fontSize: 13,
    marginBottom: 6,
  },
  value: {
    color: '#FFFFFF',
    fontSize: 17,
    fontWeight: '600',
  },
  change: {
    fontSize: 13,
    marginTop: 4,
    fontWeight: '500',
  },
});
