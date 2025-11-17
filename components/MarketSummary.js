import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';

const API = 'http://192.168.219.106:8000'; // ← 각자 자기 PC IPv4 넣기

export default function MarketSummary() {
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API}/market/summary`);
        const json = await res.json();
        setMarketData(json.data || []);
      } catch (e) {
        console.log('fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>시장 현황📊</Text>
        <ActivityIndicator color="#fff" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>시장 현황📊</Text>
      <View style={styles.row}>
        {marketData.map((item) => {
          const isUp = item.change > 0;
          return (
            <View key={item.id} style={styles.card}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.value}>
                {Number(item.value).toLocaleString()}
              </Text>
              <Text
                style={[styles.change, { color: isUp ? '#4CAF50' : '#FF5B5B' }]}
              >
                {isUp ? '↗ +' : '↘ '}
                {Number(item.change).toFixed(2)}
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
  },
  title: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 10,
  },
  row: { flexDirection: 'row', justifyContent: 'space-between' },
  card: {
    flex: 1,
    backgroundColor: '#161B2E',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  name: { color: '#B0B3C2', fontSize: 13, marginBottom: 6 },
  value: { color: '#FFFFFF', fontSize: 17, fontWeight: '600' },
  change: { fontSize: 13, marginTop: 4, fontWeight: '500' },
});
